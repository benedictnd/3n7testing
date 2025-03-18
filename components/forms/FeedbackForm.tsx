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
import { Textarea } from "@/components/ui/textarea";
import { Slider } from "@/components/ui/slider";
import { 
  Card, 
  CardContent, 
  CardDescription, 
  CardFooter, 
  CardHeader, 
  CardTitle 
} from "@/components/ui/card";
import { RadioGroup, RadioGroupItem } from "@/components/ui/radio-group";
import { Label } from "@/components/ui/label";
import { Checkbox } from "@/components/ui/checkbox";
import { Separator } from "@/components/ui/separator";
import { Check, Star } from "lucide-react";

// Feedback schema definition
const feedbackSchema = z.object({
  // Session rating
  sessionRating: z.number().min(1, { message: "Please rate the session" }).max(5),
  sessionComments: z.string().optional(),
  
  // Physical aspects
  physicalDifficulty: z.number().min(1, { message: "Please rate the physical difficulty" }).max(10),
  fatigue: z.number().min(1, { message: "Please rate your fatigue level" }).max(10),
  painAreas: z.array(z.string()).optional(),
  painLevel: z.number().min(0).max(10).optional(),
  painDescription: z.string().optional(),
  
  // Technical aspects
  technicalDifficulty: z.number().min(1, { message: "Please rate the technical difficulty" }).max(10),
  technicalImprovement: z.string().optional(),
  technicalChallenges: z.string().optional(),
  
  // Mental aspects
  mentalDifficulty: z.number().min(1, { message: "Please rate the mental difficulty" }).max(10),
  concentration: z.number().min(1, { message: "Please rate your concentration level" }).max(10),
  motivation: z.number().min(1, { message: "Please rate your motivation level" }).max(10),
  
  // Overall feedback
  enjoyed: z.enum(["yes", "partially", "no"]),
  wouldRepeat: z.enum(["yes", "maybe", "no"]),
  additionalFeedback: z.string().optional(),
});

// Body parts for pain area selection
const bodyParts = [
  "Head", "Neck", "Shoulders", "Upper back", "Lower back", "Chest", 
  "Abdomen", "Biceps", "Triceps", "Forearms", "Wrists", "Hands", 
  "Hips", "Glutes", "Quadriceps", "Hamstrings", "Calves", "Ankles", "Feet"
];

interface FeedbackFormProps {
  sessionId?: string;
  sessionName?: string;
  sessionDate?: string;
  sessionCoach?: string;
  onSuccess?: () => void;
}

export function FeedbackForm({
  sessionId = "123", // Default values for demo purposes
  sessionName = "Core Training Session",
  sessionDate = "October 10, 2023",
  sessionCoach = "Coach Smith",
  onSuccess
}: FeedbackFormProps) {
  const router = useRouter();
  const [hasPain, setHasPain] = useState(false);
  
  // Initialize form
  const form = useForm<z.infer<typeof feedbackSchema>>({
    resolver: zodResolver(feedbackSchema),
    defaultValues: {
      sessionRating: 3,
      sessionComments: "",
      physicalDifficulty: 5,
      fatigue: 5,
      painAreas: [],
      painLevel: 0,
      painDescription: "",
      technicalDifficulty: 5,
      technicalImprovement: "",
      technicalChallenges: "",
      mentalDifficulty: 5,
      concentration: 5,
      motivation: 5,
      enjoyed: "partially",
      wouldRepeat: "maybe",
      additionalFeedback: "",
    },
  });
  
  // Watch pain areas to determine if user has pain
  const painAreas = form.watch("painAreas") || [];
  
  // Update hasPain state when painAreas changes
  useState(() => {
    setHasPain(painAreas.length > 0);
  });
  
  // Form submission handler
  const onSubmit = async (values: z.infer<typeof feedbackSchema>) => {
    console.log("Feedback submitted:", values);
    
    try {
      // Demo only - would normally call API here
      // Example API call:
      // await fetch("/api/feedback", {
      //   method: "POST",
      //   headers: { "Content-Type": "application/json" },
      //   body: JSON.stringify({ sessionId, ...values }),
      // });
      
      alert("Feedback submitted successfully!");
      
      // Call onSuccess callback if provided
      if (onSuccess) {
        onSuccess();
      } else {
        // Otherwise redirect to sessions page
        router.push("/training-sessions");
      }
    } catch (error) {
      console.error("Error submitting feedback:", error);
      alert("Failed to submit feedback. Please try again.");
    }
  };
  
  return (
    <div className="container mx-auto px-4 py-8 max-w-3xl">
      <Card className="w-full">
        <CardHeader className="space-y-1">
          <CardTitle className="text-2xl font-bold text-center">Session Feedback</CardTitle>
          <CardDescription className="text-center">
            Share your experience and help us improve future sessions
          </CardDescription>
          
          {/* Session details */}
          <div className="mt-4 bg-muted rounded-lg p-4 text-sm">
            <div className="grid grid-cols-2 gap-2">
              <div>
                <p className="font-medium">Session:</p>
                <p>{sessionName}</p>
              </div>
              <div>
                <p className="font-medium">Date:</p>
                <p>{sessionDate}</p>
              </div>
              <div>
                <p className="font-medium">Coach:</p>
                <p>{sessionCoach}</p>
              </div>
              <div>
                <p className="font-medium">ID:</p>
                <p className="text-muted-foreground">{sessionId}</p>
              </div>
            </div>
          </div>
        </CardHeader>
          
        <CardContent>
          <Form {...form}>
            <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-6">
              {/* Overall Session Rating */}
              <div className="space-y-4">
                <h3 className="text-lg font-medium">Overall Session Rating</h3>
                
                <FormField
                  control={form.control}
                  name="sessionRating"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>How would you rate this session?</FormLabel>
                      <FormControl>
                        <div className="flex items-center justify-center space-x-2">
                          {[1, 2, 3, 4, 5].map((rating) => (
                            <button
                              key={rating}
                              type="button"
                              onClick={() => field.onChange(rating)}
                              className={`p-1 rounded-full focus:outline-none focus:ring-2 focus:ring-primary ${
                                field.value >= rating ? "text-yellow-500" : "text-gray-300"
                              }`}
                              aria-label={`Rate ${rating} stars`}
                            >
                              <Star className="w-8 h-8" fill={field.value >= rating ? "currentColor" : "none"} />
                            </button>
                          ))}
                        </div>
                      </FormControl>
                      <FormMessage />
                    </FormItem>
                  )}
                />
                
                <FormField
                  control={form.control}
                  name="sessionComments"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>Comments about the session</FormLabel>
                      <FormControl>
                        <Textarea
                          placeholder="What did you like or dislike about the session?"
                          className="min-h-[100px]"
                          {...field}
                        />
                      </FormControl>
                      <FormMessage />
                    </FormItem>
                  )}
                />
              </div>
              
              <Separator />
              
              {/* Physical Aspects */}
              <div className="space-y-4">
                <h3 className="text-lg font-medium">Physical Aspects</h3>
                
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <FormField
                    control={form.control}
                    name="physicalDifficulty"
                    render={({ field }) => (
                      <FormItem className="space-y-2">
                        <FormLabel>Physical Difficulty (1-10): {field.value}</FormLabel>
                        <FormControl>
                          <Slider
                            min={1}
                            max={10}
                            step={1}
                            value={[field.value]}
                            onValueChange={(value) => field.onChange(value[0])}
                          />
                        </FormControl>
                        <FormDescription className="text-xs flex justify-between">
                          <span>Very Easy</span>
                          <span>Very Difficult</span>
                        </FormDescription>
                        <FormMessage />
                      </FormItem>
                    )}
                  />
                  
                  <FormField
                    control={form.control}
                    name="fatigue"
                    render={({ field }) => (
                      <FormItem className="space-y-2">
                        <FormLabel>Fatigue Level (1-10): {field.value}</FormLabel>
                        <FormControl>
                          <Slider
                            min={1}
                            max={10}
                            step={1}
                            value={[field.value]}
                            onValueChange={(value) => field.onChange(value[0])}
                          />
                        </FormControl>
                        <FormDescription className="text-xs flex justify-between">
                          <span>Not Tired</span>
                          <span>Exhausted</span>
                        </FormDescription>
                        <FormMessage />
                      </FormItem>
                    )}
                  />
                </div>
                
                <div className="space-y-2">
                  <Label className="text-base">Did you experience pain during the session?</Label>
                  <div className="flex items-center space-x-2">
                    <Checkbox 
                      id="has-pain" 
                      checked={hasPain}
                      onCheckedChange={(checked) => {
                        setHasPain(!!checked);
                        if (!checked) {
                          form.setValue("painAreas", []);
                          form.setValue("painLevel", 0);
                          form.setValue("painDescription", "");
                        }
                      }}
                    />
                    <Label htmlFor="has-pain">Yes, I experienced pain</Label>
                  </div>
                </div>
                
                {hasPain && (
                  <div className="space-y-4 p-4 bg-muted rounded-md">
                    <FormField
                      control={form.control}
                      name="painAreas"
                      render={({ field }) => (
                        <FormItem>
                          <FormLabel>Select areas where you felt pain:</FormLabel>
                          <div className="grid grid-cols-2 md:grid-cols-3 gap-2">
                            {bodyParts.map((part) => (
                              <div key={part} className="flex items-center space-x-2">
                                <Checkbox
                                  id={`pain-${part}`}
                                  value={part}
                                  checked={(field.value || []).includes(part)}
                                  onCheckedChange={(checked) => {
                                    const currentValues = field.value || [];
                                    const updatedValues = checked
                                      ? [...currentValues, part]
                                      : currentValues.filter(value => value !== part);
                                    field.onChange(updatedValues);
                                  }}
                                />
                                <Label htmlFor={`pain-${part}`}>{part}</Label>
                              </div>
                            ))}
                          </div>
                          <FormMessage />
                        </FormItem>
                      )}
                    />
                    
                    <FormField
                      control={form.control}
                      name="painLevel"
                      render={({ field }) => (
                        <FormItem className="space-y-2">
                          <FormLabel>Pain Intensity (1-10): {field.value}</FormLabel>
                          <FormControl>
                            <Slider
                              min={1}
                              max={10}
                              step={1}
                              value={[field.value || 1]}
                              onValueChange={(value) => field.onChange(value[0])}
                            />
                          </FormControl>
                          <FormDescription className="text-xs flex justify-between">
                            <span>Mild</span>
                            <span>Severe</span>
                          </FormDescription>
                          <FormMessage />
                        </FormItem>
                      )}
                    />
                    
                    <FormField
                      control={form.control}
                      name="painDescription"
                      render={({ field }) => (
                        <FormItem>
                          <FormLabel>Describe the pain:</FormLabel>
                          <FormControl>
                            <Textarea
                              placeholder="When did it start? Is it sharp, dull, throbbing? What movements trigger it?"
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
              
              <Separator />
              
              {/* Technical Aspects */}
              <div className="space-y-4">
                <h3 className="text-lg font-medium">Technical Aspects</h3>
                
                <FormField
                  control={form.control}
                  name="technicalDifficulty"
                  render={({ field }) => (
                    <FormItem className="space-y-2">
                      <FormLabel>Technical Difficulty (1-10): {field.value}</FormLabel>
                      <FormControl>
                        <Slider
                          min={1}
                          max={10}
                          step={1}
                          value={[field.value]}
                          onValueChange={(value) => field.onChange(value[0])}
                        />
                      </FormControl>
                      <FormDescription className="text-xs flex justify-between">
                        <span>Very Easy</span>
                        <span>Very Difficult</span>
                      </FormDescription>
                      <FormMessage />
                    </FormItem>
                  )}
                />
                
                <FormField
                  control={form.control}
                  name="technicalImprovement"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>What technical skills did you improve?</FormLabel>
                      <FormControl>
                        <Textarea
                          placeholder="Which techniques or skills do you feel you improved during this session?"
                          {...field}
                        />
                      </FormControl>
                      <FormMessage />
                    </FormItem>
                  )}
                />
                
                <FormField
                  control={form.control}
                  name="technicalChallenges"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>What technical challenges did you face?</FormLabel>
                      <FormControl>
                        <Textarea
                          placeholder="Which techniques or skills were difficult for you in this session?"
                          {...field}
                        />
                      </FormControl>
                      <FormMessage />
                    </FormItem>
                  )}
                />
              </div>
              
              <Separator />
              
              {/* Mental Aspects */}
              <div className="space-y-4">
                <h3 className="text-lg font-medium">Mental Aspects</h3>
                
                <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                  <FormField
                    control={form.control}
                    name="mentalDifficulty"
                    render={({ field }) => (
                      <FormItem className="space-y-2">
                        <FormLabel>Mental Difficulty: {field.value}</FormLabel>
                        <FormControl>
                          <Slider
                            min={1}
                            max={10}
                            step={1}
                            value={[field.value]}
                            onValueChange={(value) => field.onChange(value[0])}
                          />
                        </FormControl>
                        <FormMessage />
                      </FormItem>
                    )}
                  />
                  
                  <FormField
                    control={form.control}
                    name="concentration"
                    render={({ field }) => (
                      <FormItem className="space-y-2">
                        <FormLabel>Concentration: {field.value}</FormLabel>
                        <FormControl>
                          <Slider
                            min={1}
                            max={10}
                            step={1}
                            value={[field.value]}
                            onValueChange={(value) => field.onChange(value[0])}
                          />
                        </FormControl>
                        <FormMessage />
                      </FormItem>
                    )}
                  />
                  
                  <FormField
                    control={form.control}
                    name="motivation"
                    render={({ field }) => (
                      <FormItem className="space-y-2">
                        <FormLabel>Motivation: {field.value}</FormLabel>
                        <FormControl>
                          <Slider
                            min={1}
                            max={10}
                            step={1}
                            value={[field.value]}
                            onValueChange={(value) => field.onChange(value[0])}
                          />
                        </FormControl>
                        <FormMessage />
                      </FormItem>
                    )}
                  />
                </div>
              </div>
              
              <Separator />
              
              {/* Overall Feedback */}
              <div className="space-y-4">
                <h3 className="text-lg font-medium">Overall Feedback</h3>
                
                <FormField
                  control={form.control}
                  name="enjoyed"
                  render={({ field }) => (
                    <FormItem className="space-y-2">
                      <FormLabel>Did you enjoy this session?</FormLabel>
                      <FormControl>
                        <RadioGroup
                          value={field.value}
                          onValueChange={field.onChange}
                          className="flex flex-col space-y-1"
                        >
                          <div className="flex items-center space-x-2">
                            <RadioGroupItem value="yes" id="enjoyed-yes" />
                            <Label htmlFor="enjoyed-yes">Yes, I enjoyed it a lot</Label>
                          </div>
                          <div className="flex items-center space-x-2">
                            <RadioGroupItem value="partially" id="enjoyed-partially" />
                            <Label htmlFor="enjoyed-partially">Partially, it was ok</Label>
                          </div>
                          <div className="flex items-center space-x-2">
                            <RadioGroupItem value="no" id="enjoyed-no" />
                            <Label htmlFor="enjoyed-no">No, I didn't enjoy it</Label>
                          </div>
                        </RadioGroup>
                      </FormControl>
                      <FormMessage />
                    </FormItem>
                  )}
                />
                
                <FormField
                  control={form.control}
                  name="wouldRepeat"
                  render={({ field }) => (
                    <FormItem className="space-y-2">
                      <FormLabel>Would you like to repeat this session?</FormLabel>
                      <FormControl>
                        <RadioGroup
                          value={field.value}
                          onValueChange={field.onChange}
                          className="flex flex-col space-y-1"
                        >
                          <div className="flex items-center space-x-2">
                            <RadioGroupItem value="yes" id="repeat-yes" />
                            <Label htmlFor="repeat-yes">Yes, definitely</Label>
                          </div>
                          <div className="flex items-center space-x-2">
                            <RadioGroupItem value="maybe" id="repeat-maybe" />
                            <Label htmlFor="repeat-maybe">Maybe, with some adjustments</Label>
                          </div>
                          <div className="flex items-center space-x-2">
                            <RadioGroupItem value="no" id="repeat-no" />
                            <Label htmlFor="repeat-no">No, I wouldn't</Label>
                          </div>
                        </RadioGroup>
                      </FormControl>
                      <FormMessage />
                    </FormItem>
                  )}
                />
                
                <FormField
                  control={form.control}
                  name="additionalFeedback"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>Additional Comments</FormLabel>
                      <FormControl>
                        <Textarea
                          placeholder="Any additional feedback or suggestions for improvement?"
                          className="min-h-[100px]"
                          {...field}
                        />
                      </FormControl>
                      <FormMessage />
                    </FormItem>
                  )}
                />
              </div>
              
              <div className="pt-4 flex justify-end space-x-4">
                <Button variant="outline" type="button" onClick={() => router.back()}>
                  Cancel
                </Button>
                <Button type="submit">Submit Feedback</Button>
              </div>
            </form>
          </Form>
        </CardContent>
      </Card>
    </div>
  );
} 