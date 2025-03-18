"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/router";
import Head from "next/head";
import { zodResolver } from "@hookform/resolvers/zod";
import { useForm } from "react-hook-form";
import * as z from "zod";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Card, CardContent, CardDescription, CardHeader, CardTitle, CardFooter } from "@/components/ui/card";
import { Form, FormControl, FormDescription, FormField, FormItem, FormLabel, FormMessage } from "@/components/ui/form";
import { Separator } from "@/components/ui/separator";
import API from "@/lib/api-client";

// Define athlete profile schema
const athleteProfileSchema = z.object({
  name: z.string().min(2, "Name must be at least 2 characters"),
  email: z.string().email("Invalid email address"),
  age: z.string().refine((val) => !isNaN(parseInt(val)) && parseInt(val) > 0, {
    message: "Age must be a positive number",
  }),
  height: z.string().refine((val) => !isNaN(parseFloat(val)) && parseFloat(val) > 0, {
    message: "Height must be a positive number",
  }),
  weight: z.string().refine((val) => !isNaN(parseFloat(val)) && parseFloat(val) > 0, {
    message: "Weight must be a positive number",
  }),
  sports: z.string().optional(),
  experience_level: z.string().optional(),
  injury_history: z.string().optional(),
});

type AthleteProfileFormValues = z.infer<typeof athleteProfileSchema>;

// Define coach profile schema (simpler version)
const coachProfileSchema = z.object({
  name: z.string().min(2, "Name must be at least 2 characters"),
  email: z.string().email("Invalid email address"),
  specializations: z.string().optional(),
  years_experience: z.string().optional(),
  certifications: z.string().optional(),
});

type CoachProfileFormValues = z.infer<typeof coachProfileSchema>;

export default function ProfilePage() {
  const [userData, setUserData] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);
  const router = useRouter();

  // Set up forms with our schema
  const athleteForm = useForm<AthleteProfileFormValues>({
    resolver: zodResolver(athleteProfileSchema),
    defaultValues: {
      name: "",
      email: "",
      age: "",
      height: "",
      weight: "",
      sports: "",
      experience_level: "",
      injury_history: "",
    },
  });

  const coachForm = useForm<CoachProfileFormValues>({
    resolver: zodResolver(coachProfileSchema),
    defaultValues: {
      name: "",
      email: "",
      specializations: "",
      years_experience: "",
      certifications: "",
    },
  });

  useEffect(() => {
    const fetchData = async () => {
      try {
        // Check if user is authenticated
        const token = localStorage.getItem("auth_token");
        if (!token) {
          router.push("/login");
          return;
        }

        API.setToken(token);

        // Fetch user data
        const userResponse = await API.getCurrentUser();
        if (!userResponse.success) {
          throw new Error(userResponse.error || "Failed to fetch user data");
        }

        setUserData(userResponse.data);

        // Fill the appropriate form based on user role
        if (userResponse.data.role === "athlete") {
          athleteForm.reset({
            name: userResponse.data.name || "",
            email: userResponse.data.email || "",
            age: userResponse.data.age?.toString() || "",
            height: userResponse.data.height?.toString() || "",
            weight: userResponse.data.weight?.toString() || "",
            sports: Array.isArray(userResponse.data.sports) 
              ? userResponse.data.sports.join(", ") 
              : userResponse.data.sports || "",
            experience_level: userResponse.data.experience_level || "",
            injury_history: userResponse.data.injury_history || "",
          });
        } else if (userResponse.data.role === "coach") {
          coachForm.reset({
            name: userResponse.data.name || "",
            email: userResponse.data.email || "",
            specializations: Array.isArray(userResponse.data.specializations) 
              ? userResponse.data.specializations.join(", ") 
              : userResponse.data.specializations || "",
            years_experience: userResponse.data.years_experience?.toString() || "",
            certifications: Array.isArray(userResponse.data.certifications) 
              ? userResponse.data.certifications.join(", ") 
              : userResponse.data.certifications || "",
          });
        }
      } catch (err) {
        console.error("Error fetching user data:", err);
        setError("Failed to load user profile. Please refresh or try again later.");
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [router, athleteForm, coachForm]);

  const onAthleteSubmit = async (values: AthleteProfileFormValues) => {
    setIsSubmitting(true);
    setError("");
    setSuccess("");

    try {
      // Convert string fields to appropriate types
      const updateData = {
        name: values.name,
        email: values.email,
        age: parseInt(values.age),
        height: parseFloat(values.height),
        weight: parseFloat(values.weight),
        sports: values.sports ? values.sports.split(",").map(s => s.trim()) : [],
        experience_level: values.experience_level,
        injury_history: values.injury_history,
      };

      const response = await API.updateUser(userData.id, updateData);

      if (response.success) {
        setSuccess("Profile updated successfully!");
        setUserData({
          ...userData,
          ...updateData
        });
      } else {
        setError(response.error || "Failed to update profile");
      }
    } catch (err) {
      console.error("Error updating profile:", err);
      setError("An error occurred while updating your profile");
    } finally {
      setIsSubmitting(false);
    }
  };

  const onCoachSubmit = async (values: CoachProfileFormValues) => {
    setIsSubmitting(true);
    setError("");
    setSuccess("");

    try {
      // Convert string fields to appropriate types
      const updateData = {
        name: values.name,
        email: values.email,
        specializations: values.specializations ? values.specializations.split(",").map(s => s.trim()) : [],
        years_experience: values.years_experience ? parseInt(values.years_experience) : undefined,
        certifications: values.certifications ? values.certifications.split(",").map(s => s.trim()) : [],
      };

      const response = await API.updateUser(userData.id, updateData);

      if (response.success) {
        setSuccess("Profile updated successfully!");
        setUserData({
          ...userData,
          ...updateData
        });
      } else {
        setError(response.error || "Failed to update profile");
      }
    } catch (err) {
      console.error("Error updating profile:", err);
      setError("An error occurred while updating your profile");
    } finally {
      setIsSubmitting(false);
    }
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center min-h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-primary"></div>
      </div>
    );
  }

  return (
    <div className="container mx-auto py-4 px-4 md:px-6 lg:px-8">
      <Head>
        <title>My Profile | 3&7 Training Platform</title>
      </Head>

      <div className="flex justify-between items-center mb-6">
        <h1 className="text-3xl font-bold">My Profile</h1>
        <Button onClick={() => router.push("/dashboard")}>
          Back to Dashboard
        </Button>
      </div>

      {error && (
        <div className="mb-6 p-4 bg-red-50 border border-red-200 text-red-600 rounded-md">
          {error}
        </div>
      )}

      {success && (
        <div className="mb-6 p-4 bg-green-50 border border-green-200 text-green-600 rounded-md">
          {success}
        </div>
      )}

      <Card className="mb-8">
        <CardHeader>
          <CardTitle>Account Information</CardTitle>
          <CardDescription>
            Basic account details and role information
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <p className="text-sm font-medium text-gray-500">Email</p>
              <p className="mt-1">{userData?.email}</p>
            </div>
            <div>
              <p className="text-sm font-medium text-gray-500">Role</p>
              <p className="mt-1 capitalize">{userData?.role}</p>
            </div>
          </div>
        </CardContent>
      </Card>

      <Separator className="my-8" />

      {userData?.role === "athlete" ? (
        <Card>
          <CardHeader>
            <CardTitle>Athlete Profile</CardTitle>
            <CardDescription>
              Update your athlete details including physical attributes and injury history
            </CardDescription>
          </CardHeader>
          <CardContent>
            <Form {...athleteForm}>
              <form onSubmit={athleteForm.handleSubmit(onAthleteSubmit)} className="space-y-6">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <FormField
                    control={athleteForm.control}
                    name="name"
                    render={({ field }) => (
                      <FormItem>
                        <FormLabel>Name</FormLabel>
                        <FormControl>
                          <Input {...field} />
                        </FormControl>
                        <FormMessage />
                      </FormItem>
                    )}
                  />

                  <FormField
                    control={athleteForm.control}
                    name="email"
                    render={({ field }) => (
                      <FormItem>
                        <FormLabel>Email</FormLabel>
                        <FormControl>
                          <Input {...field} />
                        </FormControl>
                        <FormMessage />
                      </FormItem>
                    )}
                  />

                  <FormField
                    control={athleteForm.control}
                    name="age"
                    render={({ field }) => (
                      <FormItem>
                        <FormLabel>Age</FormLabel>
                        <FormControl>
                          <Input {...field} type="number" />
                        </FormControl>
                        <FormMessage />
                      </FormItem>
                    )}
                  />

                  <FormField
                    control={athleteForm.control}
                    name="height"
                    render={({ field }) => (
                      <FormItem>
                        <FormLabel>Height (cm)</FormLabel>
                        <FormControl>
                          <Input {...field} type="number" step="0.1" />
                        </FormControl>
                        <FormMessage />
                      </FormItem>
                    )}
                  />

                  <FormField
                    control={athleteForm.control}
                    name="weight"
                    render={({ field }) => (
                      <FormItem>
                        <FormLabel>Weight (kg)</FormLabel>
                        <FormControl>
                          <Input {...field} type="number" step="0.1" />
                        </FormControl>
                        <FormMessage />
                      </FormItem>
                    )}
                  />

                  <FormField
                    control={athleteForm.control}
                    name="sports"
                    render={({ field }) => (
                      <FormItem>
                        <FormLabel>Sports</FormLabel>
                        <FormControl>
                          <Input {...field} placeholder="e.g. Football, Swimming" />
                        </FormControl>
                        <FormDescription>
                          Separate multiple sports with commas
                        </FormDescription>
                        <FormMessage />
                      </FormItem>
                    )}
                  />

                  <FormField
                    control={athleteForm.control}
                    name="experience_level"
                    render={({ field }) => (
                      <FormItem>
                        <FormLabel>Experience Level</FormLabel>
                        <FormControl>
                          <Input {...field} placeholder="e.g. Beginner, Intermediate, Professional" />
                        </FormControl>
                        <FormMessage />
                      </FormItem>
                    )}
                  />
                </div>

                <FormField
                  control={athleteForm.control}
                  name="injury_history"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>Injury History</FormLabel>
                      <FormControl>
                        <Textarea 
                          {...field} 
                          placeholder="Please describe any past or current injuries that may affect your training..." 
                          className="min-h-[100px]"
                        />
                      </FormControl>
                      <FormDescription>
                        This information will help coaches tailor sessions to your needs
                      </FormDescription>
                      <FormMessage />
                    </FormItem>
                  )}
                />

                <div className="flex justify-end">
                  <Button type="submit" disabled={isSubmitting}>
                    {isSubmitting ? "Saving..." : "Save Profile"}
                  </Button>
                </div>
              </form>
            </Form>
          </CardContent>
        </Card>
      ) : userData?.role === "coach" ? (
        <Card>
          <CardHeader>
            <CardTitle>Coach Profile</CardTitle>
            <CardDescription>
              Update your coaching information and credentials
            </CardDescription>
          </CardHeader>
          <CardContent>
            <Form {...coachForm}>
              <form onSubmit={coachForm.handleSubmit(onCoachSubmit)} className="space-y-6">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <FormField
                    control={coachForm.control}
                    name="name"
                    render={({ field }) => (
                      <FormItem>
                        <FormLabel>Name</FormLabel>
                        <FormControl>
                          <Input {...field} />
                        </FormControl>
                        <FormMessage />
                      </FormItem>
                    )}
                  />

                  <FormField
                    control={coachForm.control}
                    name="email"
                    render={({ field }) => (
                      <FormItem>
                        <FormLabel>Email</FormLabel>
                        <FormControl>
                          <Input {...field} />
                        </FormControl>
                        <FormMessage />
                      </FormItem>
                    )}
                  />

                  <FormField
                    control={coachForm.control}
                    name="specializations"
                    render={({ field }) => (
                      <FormItem>
                        <FormLabel>Specializations</FormLabel>
                        <FormControl>
                          <Input {...field} placeholder="e.g. Strength, Conditioning, Recovery" />
                        </FormControl>
                        <FormDescription>
                          Separate multiple specializations with commas
                        </FormDescription>
                        <FormMessage />
                      </FormItem>
                    )}
                  />

                  <FormField
                    control={coachForm.control}
                    name="years_experience"
                    render={({ field }) => (
                      <FormItem>
                        <FormLabel>Years of Experience</FormLabel>
                        <FormControl>
                          <Input {...field} type="number" />
                        </FormControl>
                        <FormMessage />
                      </FormItem>
                    )}
                  />

                  <FormField
                    control={coachForm.control}
                    name="certifications"
                    render={({ field }) => (
                      <FormItem className="col-span-2">
                        <FormLabel>Certifications</FormLabel>
                        <FormControl>
                          <Textarea 
                            {...field} 
                            placeholder="e.g. NASM-CPT, CSCS, ACE" 
                          />
                        </FormControl>
                        <FormDescription>
                          Separate multiple certifications with commas
                        </FormDescription>
                        <FormMessage />
                      </FormItem>
                    )}
                  />
                </div>

                <div className="flex justify-end">
                  <Button type="submit" disabled={isSubmitting}>
                    {isSubmitting ? "Saving..." : "Save Profile"}
                  </Button>
                </div>
              </form>
            </Form>
          </CardContent>
        </Card>
      ) : (
        <div className="text-center p-8 border rounded-md bg-gray-50">
          <p>Profile editing not available for your role.</p>
        </div>
      )}
    </div>
  );
} 