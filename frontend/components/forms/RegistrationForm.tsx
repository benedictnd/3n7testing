"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { zodResolver } from "@hookform/resolvers/zod";
import { useForm } from "react-hook-form";
import { z } from "zod";
import { 
  Form, 
  FormControl, 
  FormDescription, 
  FormField, 
  FormItem, 
  FormLabel, 
  FormMessage 
} from "@/components/ui/form";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { 
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Checkbox } from "@/components/ui/checkbox";
import { Label } from "@/components/ui/label";
import { 
  Card, 
  CardContent, 
  CardDescription, 
  CardFooter, 
  CardHeader, 
  CardTitle 
} from "@/components/ui/card";
import { Textarea } from "@/components/ui/textarea";
import { CalendarIcon, Eye, EyeOff } from "lucide-react";
import { Calendar } from "@/components/ui/calendar";
import { Popover, PopoverContent, PopoverTrigger } from "@/components/ui/popover";
import { format } from "date-fns";
import { cn } from "@/lib/utils";

// Base registration schema with common fields
const baseSchema = z.object({
  email: z.string().email({ message: "Please enter a valid email address" }),
  password: z
    .string()
    .min(8, { message: "Password must be at least 8 characters" })
    .regex(/[A-Z]/, { message: "Password must contain at least one uppercase letter" })
    .regex(/[a-z]/, { message: "Password must contain at least one lowercase letter" })
    .regex(/[0-9]/, { message: "Password must contain at least one number" }),
  confirmPassword: z.string(),
  firstName: z.string().min(1, { message: "First name is required" }),
  lastName: z.string().min(1, { message: "Last name is required" }),
  phoneNumber: z.string().optional(),
  userRole: z.enum(["athlete", "coach", "stakeholder", "support"]),
  termsAccepted: z.literal(true, {
    errorMap: () => ({ message: "You must accept terms and conditions" }),
  }),
}).refine((data) => data.password === data.confirmPassword, {
  message: "Passwords do not match",
  path: ["confirmPassword"],
});

// Athlete schema
const athleteSchema = baseSchema.extend({
  userRole: z.literal("athlete"),
  dateOfBirth: z.date({
    required_error: "Please select a date of birth",
  }),
  sports: z.array(z.string()).min(1, { message: "Please select at least one sport" }),
  experience: z.enum(["beginner", "intermediate", "advanced", "professional"]),
  goals: z.string().optional(),
  medicalConditions: z.string().optional(),
});

// Coach schema
const coachSchema = baseSchema.extend({
  userRole: z.literal("coach"),
  specialization: z.array(z.string()).min(1, { message: "Please select at least one specialization" }),
  experience: z.number().min(0, { message: "Experience must be a valid number" }),
  certifications: z.string().optional(),
  biography: z.string().optional(),
});

// Stakeholder schema
const stakeholderSchema = baseSchema.extend({
  userRole: z.literal("stakeholder"),
  organization: z.string().min(1, { message: "Organization name is required" }),
  role: z.string().min(1, { message: "Your role in the organization is required" }),
  interests: z.array(z.string()).optional(),
});

// Support Staff schema
const supportSchema = baseSchema.extend({
  userRole: z.literal("support"),
  specialization: z.string().min(1, { message: "Specialization is required" }),
  qualifications: z.string().min(1, { message: "Qualifications are required" }),
  experience: z.number().min(0, { message: "Experience must be a valid number" }),
  availability: z.string().optional(),
});

// Combined schema
const registrationSchema = z.discriminatedUnion("userRole", [
  athleteSchema,
  coachSchema,
  stakeholderSchema,
  supportSchema,
]);

// Sports options for athletes
const sportsOptions = [
  "Football", "Basketball", "Tennis", "Swimming", "Athletics", 
  "Volleyball", "Rugby", "Hockey", "Cycling", "Golf",
  "Martial Arts", "Gymnastics", "Cricket", "Baseball", "Badminton"
];

// Specialization options for coaches
const specializationOptions = [
  "Strength & Conditioning", "Technical Coaching", "Physical Therapy", 
  "Mental Training", "Tactical Development", "Nutrition", 
  "Performance Analysis", "Injury Rehabilitation"
];

// Interest options for stakeholders
const interestOptions = [
  "Athlete Development", "Team Performance", "Club Management", 
  "Sponsorship", "Community Outreach", "Competition Organization", 
  "Facility Management", "Sports Science Research"
];

export function RegistrationForm() {
  const router = useRouter();
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  
  // Initialize form with default role as athlete
  const form = useForm<z.infer<typeof registrationSchema>>({
    resolver: zodResolver(registrationSchema),
    defaultValues: {
      userRole: "athlete",
      email: "",
      password: "",
      confirmPassword: "",
      firstName: "",
      lastName: "",
      phoneNumber: "",
      termsAccepted: false,
    },
  });
  
  // Watch for the user role to conditionally render fields
  const userRole = form.watch("userRole");
  
  // Form submission handler
  const onSubmit = async (values: z.infer<typeof registrationSchema>) => {
    console.log("Registration submitted:", values);
    
    try {
      // Demo only - would normally call API here
      // Example API call:
      // await fetch("/api/register", {
      //   method: "POST",
      //   headers: { "Content-Type": "application/json" },
      //   body: JSON.stringify(values),
      // });
      
      alert("Registration successful!");
      
      // Redirect to login page
      router.push("/login");
    } catch (error) {
      console.error("Error registering:", error);
      alert("Registration failed. Please try again.");
    }
  };
  
  return (
    <div className="container mx-auto px-4 py-8 max-w-3xl">
      <Card className="w-full">
        <CardHeader className="space-y-1">
          <CardTitle className="text-2xl font-bold text-center">Create an Account</CardTitle>
          <CardDescription className="text-center">
            Enter your information to create an account
          </CardDescription>
        </CardHeader>
          
        <CardContent>
          <Form {...form}>
            <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-6">
              {/* User Role Selection */}
              <FormField
                control={form.control}
                name="userRole"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>I am registering as a</FormLabel>
                    <Select 
                      onValueChange={(value: "athlete" | "coach" | "stakeholder" | "support") => {
                        field.onChange(value);
                        // Reset form when role changes
                        form.reset({
                          ...form.getValues(),
                          userRole: value,
                        });
                      }} 
                      defaultValue={field.value}
                    >
                      <FormControl>
                        <SelectTrigger>
                          <SelectValue placeholder="Select your role" />
                        </SelectTrigger>
                      </FormControl>
                      <SelectContent>
                        <SelectItem value="athlete">Athlete</SelectItem>
                        <SelectItem value="coach">Coach</SelectItem>
                        <SelectItem value="stakeholder">Stakeholder</SelectItem>
                        <SelectItem value="support">Support Staff</SelectItem>
                      </SelectContent>
                    </Select>
                    <FormDescription>
                      Your role determines the information we need and the features you'll access.
                    </FormDescription>
                    <FormMessage />
                  </FormItem>
                )}
              />
              
              {/* Basic Information */}
              <div className="space-y-4">
                <h3 className="text-lg font-medium">Basic Information</h3>
                
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <FormField
                    control={form.control}
                    name="firstName"
                    render={({ field }) => (
                      <FormItem>
                        <FormLabel>First Name</FormLabel>
                        <FormControl>
                          <Input placeholder="John" {...field} />
                        </FormControl>
                        <FormMessage />
                      </FormItem>
                    )}
                  />
                  
                  <FormField
                    control={form.control}
                    name="lastName"
                    render={({ field }) => (
                      <FormItem>
                        <FormLabel>Last Name</FormLabel>
                        <FormControl>
                          <Input placeholder="Doe" {...field} />
                        </FormControl>
                        <FormMessage />
                      </FormItem>
                    )}
                  />
                </div>
                
                <FormField
                  control={form.control}
                  name="email"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>Email</FormLabel>
                      <FormControl>
                        <Input type="email" placeholder="your.email@example.com" {...field} />
                      </FormControl>
                      <FormMessage />
                    </FormItem>
                  )}
                />
                
                <FormField
                  control={form.control}
                  name="phoneNumber"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>Phone Number (optional)</FormLabel>
                      <FormControl>
                        <Input placeholder="+1 234 567 8901" {...field} />
                      </FormControl>
                      <FormMessage />
                    </FormItem>
                  )}
                />
                
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <FormField
                    control={form.control}
                    name="password"
                    render={({ field }) => (
                      <FormItem>
                        <FormLabel>Password</FormLabel>
                        <FormControl>
                          <div className="relative">
                            <Input
                              type={showPassword ? "text" : "password"}
                              placeholder="••••••••"
                              {...field}
                            />
                            <button
                              type="button"
                              onClick={() => setShowPassword(!showPassword)}
                              className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-500 hover:text-gray-700"
                              aria-label={showPassword ? "Hide password" : "Show password"}
                            >
                              {showPassword ? (
                                <EyeOff className="h-4 w-4" />
                              ) : (
                                <Eye className="h-4 w-4" />
                              )}
                            </button>
                          </div>
                        </FormControl>
                        <FormDescription>
                          Must be at least 8 characters with uppercase, lowercase, and number.
                        </FormDescription>
                        <FormMessage />
                      </FormItem>
                    )}
                  />
                  
                  <FormField
                    control={form.control}
                    name="confirmPassword"
                    render={({ field }) => (
                      <FormItem>
                        <FormLabel>Confirm Password</FormLabel>
                        <FormControl>
                          <div className="relative">
                            <Input
                              type={showConfirmPassword ? "text" : "password"}
                              placeholder="••••••••"
                              {...field}
                            />
                            <button
                              type="button"
                              onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                              className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-500 hover:text-gray-700"
                              aria-label={showConfirmPassword ? "Hide password" : "Show password"}
                            >
                              {showConfirmPassword ? (
                                <EyeOff className="h-4 w-4" />
                              ) : (
                                <Eye className="h-4 w-4" />
                              )}
                            </button>
                          </div>
                        </FormControl>
                        <FormMessage />
                      </FormItem>
                    )}
                  />
                </div>
              </div>
              
              {/* Role-specific Information */}
              <div className="space-y-4">
                <h3 className="text-lg font-medium">Role-specific Information</h3>
                
                {/* Athlete Fields */}
                {userRole === "athlete" && (
                  <div className="space-y-4">
                    <FormField
                      control={form.control}
                      name="dateOfBirth"
                      render={({ field }) => (
                        <FormItem className="flex flex-col">
                          <FormLabel>Date of Birth</FormLabel>
                          <Popover>
                            <PopoverTrigger asChild>
                              <FormControl>
                                <Button
                                  variant="outline"
                                  className={cn(
                                    "w-full pl-3 text-left font-normal",
                                    !field.value && "text-muted-foreground"
                                  )}
                                >
                                  {field.value ? (
                                    format(field.value, "PPP")
                                  ) : (
                                    <span>Pick a date</span>
                                  )}
                                  <CalendarIcon className="ml-auto h-4 w-4 opacity-50" />
                                </Button>
                              </FormControl>
                            </PopoverTrigger>
                            <PopoverContent className="w-auto p-0" align="start">
                              <Calendar
                                mode="single"
                                selected={field.value}
                                onSelect={field.onChange}
                                disabled={(date) => date > new Date()}
                                initialFocus
                              />
                            </PopoverContent>
                          </Popover>
                          <FormMessage />
                        </FormItem>
                      )}
                    />
                    
                    <FormField
                      control={form.control}
                      name="sports"
                      render={({ field }) => (
                        <FormItem>
                          <FormLabel>Sports</FormLabel>
                          <FormDescription>
                            Select the sports you participate in.
                          </FormDescription>
                          <div className="grid grid-cols-2 md:grid-cols-3 gap-2 mt-2">
                            {sportsOptions.map((sport) => (
                              <div key={sport} className="flex items-center space-x-2">
                                <Checkbox
                                  id={`sport-${sport}`}
                                  value={sport}
                                  checked={(field.value || []).includes(sport)}
                                  onCheckedChange={(checked) => {
                                    const currentValues = field.value || [];
                                    const updatedValues = checked
                                      ? [...currentValues, sport]
                                      : currentValues.filter(value => value !== sport);
                                    field.onChange(updatedValues);
                                  }}
                                />
                                <Label htmlFor={`sport-${sport}`}>{sport}</Label>
                              </div>
                            ))}
                          </div>
                          <FormMessage />
                        </FormItem>
                      )}
                    />
                    
                    <FormField
                      control={form.control}
                      name="experience"
                      render={({ field }) => (
                        <FormItem>
                          <FormLabel>Experience Level</FormLabel>
                          <Select 
                            onValueChange={field.onChange} 
                            defaultValue={field.value}
                          >
                            <FormControl>
                              <SelectTrigger>
                                <SelectValue placeholder="Select your experience level" />
                              </SelectTrigger>
                            </FormControl>
                            <SelectContent>
                              <SelectItem value="beginner">Beginner</SelectItem>
                              <SelectItem value="intermediate">Intermediate</SelectItem>
                              <SelectItem value="advanced">Advanced</SelectItem>
                              <SelectItem value="professional">Professional</SelectItem>
                            </SelectContent>
                          </Select>
                          <FormMessage />
                        </FormItem>
                      )}
                    />
                    
                    <FormField
                      control={form.control}
                      name="goals"
                      render={({ field }) => (
                        <FormItem>
                          <FormLabel>Your Goals (optional)</FormLabel>
                          <FormControl>
                            <Textarea 
                              placeholder="What are you looking to achieve?"
                              className="min-h-[100px]"
                              {...field} 
                            />
                          </FormControl>
                          <FormMessage />
                        </FormItem>
                      )}
                    />
                    
                    <FormField
                      control={form.control}
                      name="medicalConditions"
                      render={({ field }) => (
                        <FormItem>
                          <FormLabel>Medical Conditions (optional)</FormLabel>
                          <FormControl>
                            <Textarea 
                              placeholder="Any medical conditions we should be aware of?"
                              className="min-h-[100px]"
                              {...field} 
                            />
                          </FormControl>
                          <FormDescription>
                            This information will be kept confidential and only shared with relevant staff.
                          </FormDescription>
                          <FormMessage />
                        </FormItem>
                      )}
                    />
                  </div>
                )}
                
                {/* Coach Fields */}
                {userRole === "coach" && (
                  <div className="space-y-4">
                    <FormField
                      control={form.control}
                      name="specialization"
                      render={({ field }) => (
                        <FormItem>
                          <FormLabel>Specializations</FormLabel>
                          <FormDescription>
                            Select your areas of expertise.
                          </FormDescription>
                          <div className="grid grid-cols-1 md:grid-cols-2 gap-2 mt-2">
                            {specializationOptions.map((spec) => (
                              <div key={spec} className="flex items-center space-x-2">
                                <Checkbox
                                  id={`spec-${spec}`}
                                  value={spec}
                                  checked={(field.value || []).includes(spec)}
                                  onCheckedChange={(checked) => {
                                    const currentValues = field.value || [];
                                    const updatedValues = checked
                                      ? [...currentValues, spec]
                                      : currentValues.filter(value => value !== spec);
                                    field.onChange(updatedValues);
                                  }}
                                />
                                <Label htmlFor={`spec-${spec}`}>{spec}</Label>
                              </div>
                            ))}
                          </div>
                          <FormMessage />
                        </FormItem>
                      )}
                    />
                    
                    <FormField
                      control={form.control}
                      name="experience"
                      render={({ field }) => (
                        <FormItem>
                          <FormLabel>Years of Experience</FormLabel>
                          <FormControl>
                            <Input 
                              type="number"
                              min="0"
                              {...field}
                              onChange={(e) => field.onChange(e.target.valueAsNumber)}
                            />
                          </FormControl>
                          <FormMessage />
                        </FormItem>
                      )}
                    />
                    
                    <FormField
                      control={form.control}
                      name="certifications"
                      render={({ field }) => (
                        <FormItem>
                          <FormLabel>Certifications (optional)</FormLabel>
                          <FormControl>
                            <Textarea 
                              placeholder="List your relevant certifications"
                              className="min-h-[100px]"
                              {...field} 
                            />
                          </FormControl>
                          <FormMessage />
                        </FormItem>
                      )}
                    />
                    
                    <FormField
                      control={form.control}
                      name="biography"
                      render={({ field }) => (
                        <FormItem>
                          <FormLabel>Professional Biography (optional)</FormLabel>
                          <FormControl>
                            <Textarea 
                              placeholder="Tell us about your coaching experience and philosophy"
                              className="min-h-[150px]"
                              {...field} 
                            />
                          </FormControl>
                          <FormMessage />
                        </FormItem>
                      )}
                    />
                  </div>
                )}
                
                {/* Stakeholder Fields */}
                {userRole === "stakeholder" && (
                  <div className="space-y-4">
                    <FormField
                      control={form.control}
                      name="organization"
                      render={({ field }) => (
                        <FormItem>
                          <FormLabel>Organization</FormLabel>
                          <FormControl>
                            <Input placeholder="Organization name" {...field} />
                          </FormControl>
                          <FormMessage />
                        </FormItem>
                      )}
                    />
                    
                    <FormField
                      control={form.control}
                      name="role"
                      render={({ field }) => (
                        <FormItem>
                          <FormLabel>Your Role in Organization</FormLabel>
                          <FormControl>
                            <Input placeholder="e.g. Director, Manager, Sponsor" {...field} />
                          </FormControl>
                          <FormMessage />
                        </FormItem>
                      )}
                    />
                    
                    <FormField
                      control={form.control}
                      name="interests"
                      render={({ field }) => (
                        <FormItem>
                          <FormLabel>Areas of Interest</FormLabel>
                          <FormDescription>
                            Select areas you're most interested in.
                          </FormDescription>
                          <div className="grid grid-cols-1 md:grid-cols-2 gap-2 mt-2">
                            {interestOptions.map((interest) => (
                              <div key={interest} className="flex items-center space-x-2">
                                <Checkbox
                                  id={`interest-${interest}`}
                                  value={interest}
                                  checked={(field.value || []).includes(interest)}
                                  onCheckedChange={(checked) => {
                                    const currentValues = field.value || [];
                                    const updatedValues = checked
                                      ? [...currentValues, interest]
                                      : currentValues.filter(value => value !== interest);
                                    field.onChange(updatedValues);
                                  }}
                                />
                                <Label htmlFor={`interest-${interest}`}>{interest}</Label>
                              </div>
                            ))}
                          </div>
                          <FormMessage />
                        </FormItem>
                      )}
                    />
                  </div>
                )}
                
                {/* Support Staff Fields */}
                {userRole === "support" && (
                  <div className="space-y-4">
                    <FormField
                      control={form.control}
                      name="specialization"
                      render={({ field }) => (
                        <FormItem>
                          <FormLabel>Specialization</FormLabel>
                          <FormControl>
                            <Input placeholder="e.g. Physiotherapist, Nutritionist" {...field} />
                          </FormControl>
                          <FormMessage />
                        </FormItem>
                      )}
                    />
                    
                    <FormField
                      control={form.control}
                      name="qualifications"
                      render={({ field }) => (
                        <FormItem>
                          <FormLabel>Qualifications</FormLabel>
                          <FormControl>
                            <Textarea 
                              placeholder="List your qualifications and credentials"
                              className="min-h-[100px]"
                              {...field} 
                            />
                          </FormControl>
                          <FormMessage />
                        </FormItem>
                      )}
                    />
                    
                    <FormField
                      control={form.control}
                      name="experience"
                      render={({ field }) => (
                        <FormItem>
                          <FormLabel>Years of Experience</FormLabel>
                          <FormControl>
                            <Input 
                              type="number"
                              min="0"
                              {...field}
                              onChange={(e) => field.onChange(e.target.valueAsNumber)}
                            />
                          </FormControl>
                          <FormMessage />
                        </FormItem>
                      )}
                    />
                    
                    <FormField
                      control={form.control}
                      name="availability"
                      render={({ field }) => (
                        <FormItem>
                          <FormLabel>Availability (optional)</FormLabel>
                          <FormControl>
                            <Textarea 
                              placeholder="Describe your typical availability (days/hours)"
                              className="min-h-[100px]"
                              {...field} 
                            />
                          </FormControl>
                          <FormMessage />
                        </FormItem>
                      )}
                    />
                  </div>
                )}
              </div>
              
              {/* Terms and Conditions */}
              <FormField
                control={form.control}
                name="termsAccepted"
                render={({ field }) => (
                  <FormItem className="flex flex-row items-start space-x-3 space-y-0">
                    <FormControl>
                      <Checkbox
                        checked={field.value}
                        onCheckedChange={field.onChange}
                      />
                    </FormControl>
                    <div className="space-y-1 leading-none">
                      <FormLabel>
                        I accept the <a href="/terms" className="text-primary underline">terms and conditions</a> and <a href="/privacy" className="text-primary underline">privacy policy</a>
                      </FormLabel>
                      <FormMessage />
                    </div>
                  </FormItem>
                )}
              />
              
              <div className="pt-4 flex justify-end space-x-4">
                <Button variant="outline" type="button" onClick={() => router.back()}>
                  Cancel
                </Button>
                <Button type="submit">Register</Button>
              </div>
            </form>
          </Form>
        </CardContent>
      </Card>
    </div>
  );
} 