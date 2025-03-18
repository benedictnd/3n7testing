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
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { 
  Card, 
  CardContent, 
  CardDescription, 
  CardFooter, 
  CardHeader, 
  CardTitle 
} from "@/components/ui/card";
import { Textarea } from "@/components/ui/textarea";
import { Label } from "@/components/ui/label";
import { Slider } from "@/components/ui/slider";
import { Checkbox } from "@/components/ui/checkbox";
import { Separator } from "@/components/ui/separator";
import { Calendar } from "@/components/ui/calendar";
import { Popover, PopoverContent, PopoverTrigger } from "@/components/ui/popover";
import { format } from "date-fns";
import { CalendarIcon, Plus, X } from "lucide-react";

// Training session schema definition
const trainingSessionSchema = z.object({
  // Basic info
  title: z.string().min(1, { message: "Title is required" }),
  type: z.enum(["core", "endurance", "recovery", "technical", "tactical", "match"]),
  date: z.date(),
  startTime: z.string().min(1, { message: "Start time is required" }),
  endTime: z.string().min(1, { message: "End time is required" }),
  location: z.string().min(1, { message: "Location is required" }),
  
  // Warming up
  warmingUpDuration: z.number().min(5, { message: "Minimum 5 minutes" }).max(30, { message: "Maximum 30 minutes" }),
  warmingUpNotes: z.string().optional(),
  
  // Main training
  mainTrainingDuration: z.number().min(20, { message: "Minimum 20 minutes" }).max(120, { message: "Maximum 120 minutes" }),
  mainTrainingNotes: z.string().optional(),
  mainTrainingIntensity: z.number().min(1, { message: "Minimum intensity 1" }).max(10, { message: "Maximum intensity 10" }),
  mainTrainingExercises: z.array(z.object({
    name: z.string().min(1, { message: "Exercise name is required" }),
    sets: z.number().min(1, { message: "Minimum 1 set" }).optional(),
    reps: z.number().min(1, { message: "Minimum 1 rep" }).optional(),
    duration: z.number().min(1, { message: "Minimum 1 minute" }).optional(),
    notes: z.string().optional(),
  })).min(1, { message: "At least one exercise is required" }),
  
  // Cooling down
  coolingDownDuration: z.number().min(5, { message: "Minimum 5 minutes" }).max(30, { message: "Maximum 30 minutes" }),
  coolingDownNotes: z.string().optional(),
  
  // Additional info
  objectives: z.string().min(5, { message: "Training objectives are required" }),
  equipment: z.array(z.string()).optional(),
  targetAudience: z.enum(["all", "specific"]),
  specificAthletes: z.array(z.string()).optional(),
  notes: z.string().optional(),
});

// Default exercise template for adding new exercises
const defaultExercise = {
  name: "",
  sets: 3,
  reps: 10,
  duration: 0,
  notes: "",
};

// Equipment options
const equipmentOptions = [
  "Cones", "Balls", "Agility ladders", "Hurdles", "Resistance bands", 
  "Weights", "Training dummies", "Bibs/Jerseys", "Goals", "Mats",
  "Timing system", "Heart rate monitors", "GPS trackers", "Jump ropes"
];

// Athlete options (would be fetched from API in a real app)
const athleteOptions = [
  { id: "1", name: "John Doe" },
  { id: "2", name: "Jane Smith" },
  { id: "3", name: "Mike Johnson" },
  { id: "4", name: "Sarah Williams" },
  { id: "5", name: "David Lee" },
  { id: "6", name: "Emma Brown" },
  { id: "7", name: "James Wilson" },
  { id: "8", name: "Olivia Moore" },
];

export function TrainingSessionForm() {
  const router = useRouter();
  const [currentTab, setCurrentTab] = useState("basic");
  
  // Initialize form
  const form = useForm<z.infer<typeof trainingSessionSchema>>({
    resolver: zodResolver(trainingSessionSchema),
    defaultValues: {
      title: "",
      type: "core",
      date: new Date(),
      startTime: "09:00",
      endTime: "11:00",
      location: "",
      warmingUpDuration: 15,
      warmingUpNotes: "",
      mainTrainingDuration: 60,
      mainTrainingNotes: "",
      mainTrainingIntensity: 7,
      mainTrainingExercises: [{ ...defaultExercise, name: "Warm-up drill" }],
      coolingDownDuration: 15,
      coolingDownNotes: "",
      objectives: "",
      equipment: [],
      targetAudience: "all",
      specificAthletes: [],
      notes: "",
    },
  });
  
  // Add a new exercise
  const addExercise = () => {
    const exercises = form.getValues("mainTrainingExercises") || [];
    form.setValue("mainTrainingExercises", [...exercises, { ...defaultExercise }]);
  };
  
  // Remove an exercise
  const removeExercise = (index: number) => {
    const exercises = form.getValues("mainTrainingExercises") || [];
    form.setValue(
      "mainTrainingExercises",
      exercises.filter((_, i) => i !== index)
    );
  };

  // Form submission handler
  const onSubmit = async (values: z.infer<typeof trainingSessionSchema>) => {
    console.log("Form submitted:", values);
    
    // Demo only - would normally call API here
    alert("Training session created successfully!");
    
    // Redirect to sessions page
    router.push("/training-sessions");
  };

  return (
    <div className="container mx-auto px-4 py-8 max-w-4xl">
      <Tabs
        defaultValue="basic"
        onValueChange={(value) => setCurrentTab(value)}
        className="w-full"
      >
        <div className="space-y-4">
          <h1 className="text-3xl font-bold text-center">Create Training Session</h1>
          <p className="text-muted-foreground text-center">
            Design comprehensive training sessions for your athletes.
          </p>
          
          <TabsList className="grid grid-cols-4 w-full">
            <TabsTrigger value="basic">Basic Info</TabsTrigger>
            <TabsTrigger value="warmup">Warming Up</TabsTrigger>
            <TabsTrigger value="main">Main Training</TabsTrigger>
            <TabsTrigger value="cooldown">Cooling Down</TabsTrigger>
          </TabsList>
          
          <Card>
            <Form {...form}>
              <form onSubmit={form.handleSubmit(onSubmit)}>
                {/* Basic Information */}
                <TabsContent value="basic">
                  <CardHeader>
                    <CardTitle>Basic Information</CardTitle>
                    <CardDescription>
                      Provide essential details about the training session.
                    </CardDescription>
                  </CardHeader>
                  
                  <CardContent className="space-y-4">
                    <FormField
                      control={form.control}
                      name="title"
                      render={({ field }) => (
                        <FormItem>
                          <FormLabel>Session Title</FormLabel>
                          <FormControl>
                            <Input placeholder="Weekly Core Training" {...field} />
                          </FormControl>
                          <FormMessage />
                        </FormItem>
                      )}
                    />
                    
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      <FormField
                        control={form.control}
                        name="type"
                        render={({ field }) => (
                          <FormItem>
                            <FormLabel>Session Type</FormLabel>
                            <Select 
                              onValueChange={field.onChange} 
                              defaultValue={field.value}
                            >
                              <FormControl>
                                <SelectTrigger>
                                  <SelectValue placeholder="Select type" />
                                </SelectTrigger>
                              </FormControl>
                              <SelectContent>
                                <SelectItem value="core">Core Training</SelectItem>
                                <SelectItem value="endurance">Endurance</SelectItem>
                                <SelectItem value="recovery">Recovery</SelectItem>
                                <SelectItem value="technical">Technical</SelectItem>
                                <SelectItem value="tactical">Tactical</SelectItem>
                                <SelectItem value="match">Match Preparation</SelectItem>
                              </SelectContent>
                            </Select>
                            <FormMessage />
                          </FormItem>
                        )}
                      />
                      
                      <FormField
                        control={form.control}
                        name="location"
                        render={({ field }) => (
                          <FormItem>
                            <FormLabel>Location</FormLabel>
                            <FormControl>
                              <Input placeholder="Training Ground" {...field} />
                            </FormControl>
                            <FormMessage />
                          </FormItem>
                        )}
                      />
                    </div>
                    
                    <FormField
                      control={form.control}
                      name="date"
                      render={({ field }) => (
                        <FormItem className="flex flex-col">
                          <FormLabel>Date</FormLabel>
                          <Popover>
                            <PopoverTrigger asChild>
                              <FormControl>
                                <Button
                                  variant="outline"
                                  className="w-full pl-3 text-left font-normal"
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
                                initialFocus
                              />
                            </PopoverContent>
                          </Popover>
                          <FormMessage />
                        </FormItem>
                      )}
                    />
                    
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      <FormField
                        control={form.control}
                        name="startTime"
                        render={({ field }) => (
                          <FormItem>
                            <FormLabel>Start Time</FormLabel>
                            <FormControl>
                              <Input type="time" {...field} />
                            </FormControl>
                            <FormMessage />
                          </FormItem>
                        )}
                      />
                      
                      <FormField
                        control={form.control}
                        name="endTime"
                        render={({ field }) => (
                          <FormItem>
                            <FormLabel>End Time</FormLabel>
                            <FormControl>
                              <Input type="time" {...field} />
                            </FormControl>
                            <FormMessage />
                          </FormItem>
                        )}
                      />
                    </div>
                    
                    <FormField
                      control={form.control}
                      name="objectives"
                      render={({ field }) => (
                        <FormItem>
                          <FormLabel>Session Objectives</FormLabel>
                          <FormControl>
                            <Textarea
                              placeholder="Describe the main objectives of this training session..."
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
                      name="targetAudience"
                      render={({ field }) => (
                        <FormItem className="space-y-3">
                          <FormLabel>Target Audience</FormLabel>
                          <FormControl>
                            <div className="flex flex-col space-y-2">
                              <div className="flex items-center space-x-2">
                                <input
                                  type="radio"
                                  id="all-athletes"
                                  value="all"
                                  checked={field.value === "all"}
                                  onChange={() => form.setValue("targetAudience", "all")}
                                  className="h-4 w-4"
                                />
                                <Label htmlFor="all-athletes">All Athletes</Label>
                              </div>
                              <div className="flex items-center space-x-2">
                                <input
                                  type="radio"
                                  id="specific-athletes"
                                  value="specific"
                                  checked={field.value === "specific"}
                                  onChange={() => form.setValue("targetAudience", "specific")}
                                  className="h-4 w-4"
                                />
                                <Label htmlFor="specific-athletes">Specific Athletes</Label>
                              </div>
                            </div>
                          </FormControl>
                          <FormMessage />
                        </FormItem>
                      )}
                    />
                    
                    {form.watch("targetAudience") === "specific" && (
                      <FormField
                        control={form.control}
                        name="specificAthletes"
                        render={({ field }) => (
                          <FormItem>
                            <FormLabel>Select Athletes</FormLabel>
                            <div className="grid grid-cols-2 md:grid-cols-3 gap-2">
                              {athleteOptions.map((athlete) => (
                                <div key={athlete.id} className="flex items-center space-x-2">
                                  <Checkbox
                                    id={`athlete-${athlete.id}`}
                                    value={athlete.id}
                                    checked={(field.value || []).includes(athlete.id)}
                                    onCheckedChange={(checked) => {
                                      const currentValues = field.value || [];
                                      const updatedValues = checked
                                        ? [...currentValues, athlete.id]
                                        : currentValues.filter(value => value !== athlete.id);
                                      form.setValue("specificAthletes", updatedValues);
                                    }}
                                  />
                                  <Label htmlFor={`athlete-${athlete.id}`}>{athlete.name}</Label>
                                </div>
                              ))}
                            </div>
                            <FormMessage />
                          </FormItem>
                        )}
                      />
                    )}
                    
                    <FormField
                      control={form.control}
                      name="equipment"
                      render={({ field }) => (
                        <FormItem>
                          <FormLabel>Required Equipment</FormLabel>
                          <div className="grid grid-cols-2 md:grid-cols-3 gap-2">
                            {equipmentOptions.map((equipment) => (
                              <div key={equipment} className="flex items-center space-x-2">
                                <Checkbox
                                  id={`equipment-${equipment}`}
                                  value={equipment}
                                  checked={(field.value || []).includes(equipment)}
                                  onCheckedChange={(checked) => {
                                    const currentValues = field.value || [];
                                    const updatedValues = checked
                                      ? [...currentValues, equipment]
                                      : currentValues.filter(value => value !== equipment);
                                    form.setValue("equipment", updatedValues);
                                  }}
                                />
                                <Label htmlFor={`equipment-${equipment}`}>{equipment}</Label>
                              </div>
                            ))}
                          </div>
                          <FormMessage />
                        </FormItem>
                      )}
                    />
                  </CardContent>
                  
                  <CardFooter className="flex justify-between">
                    <Button variant="outline" type="button">
                      Cancel
                    </Button>
                    <Button type="button" onClick={() => setCurrentTab("warmup")}>
                      Next
                    </Button>
                  </CardFooter>
                </TabsContent>
                
                {/* Warming Up */}
                <TabsContent value="warmup">
                  <CardHeader>
                    <CardTitle>Warming Up</CardTitle>
                    <CardDescription>
                      Define the warm-up phase of the training session.
                    </CardDescription>
                  </CardHeader>
                  
                  <CardContent className="space-y-4">
                    <FormField
                      control={form.control}
                      name="warmingUpDuration"
                      render={({ field }) => (
                        <FormItem>
                          <FormLabel>Duration (minutes): {field.value}</FormLabel>
                          <FormControl>
                            <Slider
                              min={5}
                              max={30}
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
                      name="warmingUpNotes"
                      render={({ field }) => (
                        <FormItem>
                          <FormLabel>Warm-up Description</FormLabel>
                          <FormControl>
                            <Textarea
                              placeholder="Describe the warm-up activities, exercises and goals..."
                              className="min-h-[150px]"
                              {...field}
                            />
                          </FormControl>
                          <FormMessage />
                        </FormItem>
                      )}
                    />
                  </CardContent>
                  
                  <CardFooter className="flex justify-between">
                    <Button variant="outline" type="button" onClick={() => setCurrentTab("basic")}>
                      Previous
                    </Button>
                    <Button type="button" onClick={() => setCurrentTab("main")}>
                      Next
                    </Button>
                  </CardFooter>
                </TabsContent>
                
                {/* Main Training */}
                <TabsContent value="main">
                  <CardHeader>
                    <CardTitle>Main Training</CardTitle>
                    <CardDescription>
                      Define the core part of the training session.
                    </CardDescription>
                  </CardHeader>
                  
                  <CardContent className="space-y-6">
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      <FormField
                        control={form.control}
                        name="mainTrainingDuration"
                        render={({ field }) => (
                          <FormItem>
                            <FormLabel>Duration (minutes): {field.value}</FormLabel>
                            <FormControl>
                              <Slider
                                min={20}
                                max={120}
                                step={5}
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
                        name="mainTrainingIntensity"
                        render={({ field }) => (
                          <FormItem>
                            <FormLabel>Intensity (1-10): {field.value}</FormLabel>
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
                    
                    <FormField
                      control={form.control}
                      name="mainTrainingNotes"
                      render={({ field }) => (
                        <FormItem>
                          <FormLabel>Overview</FormLabel>
                          <FormControl>
                            <Textarea
                              placeholder="Provide a general overview of the main training phase..."
                              className="min-h-[100px]"
                              {...field}
                            />
                          </FormControl>
                          <FormMessage />
                        </FormItem>
                      )}
                    />
                    
                    <div className="space-y-4">
                      <div className="flex items-center justify-between">
                        <h3 className="text-lg font-medium">Exercises</h3>
                        <Button
                          type="button"
                          variant="outline"
                          size="sm"
                          onClick={addExercise}
                          className="flex items-center gap-1"
                        >
                          <Plus className="h-4 w-4" /> Add Exercise
                        </Button>
                      </div>
                      
                      <div className="space-y-4">
                        {form.watch("mainTrainingExercises")?.map((_, index) => (
                          <div key={index} className="rounded-md border p-4">
                            <div className="flex justify-between items-start mb-2">
                              <h4 className="font-medium">Exercise {index + 1}</h4>
                              <Button
                                type="button"
                                variant="ghost"
                                size="sm"
                                onClick={() => removeExercise(index)}
                                className="h-8 w-8 p-0"
                              >
                                <X className="h-4 w-4" />
                              </Button>
                            </div>
                            
                            <div className="space-y-4">
                              <FormField
                                control={form.control}
                                name={`mainTrainingExercises.${index}.name`}
                                render={({ field }) => (
                                  <FormItem>
                                    <FormLabel>Exercise Name</FormLabel>
                                    <FormControl>
                                      <Input placeholder="Exercise name" {...field} />
                                    </FormControl>
                                    <FormMessage />
                                  </FormItem>
                                )}
                              />
                              
                              <div className="grid grid-cols-3 gap-4">
                                <FormField
                                  control={form.control}
                                  name={`mainTrainingExercises.${index}.sets`}
                                  render={({ field }) => (
                                    <FormItem>
                                      <FormLabel>Sets</FormLabel>
                                      <FormControl>
                                        <Input
                                          type="number"
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
                                  name={`mainTrainingExercises.${index}.reps`}
                                  render={({ field }) => (
                                    <FormItem>
                                      <FormLabel>Reps</FormLabel>
                                      <FormControl>
                                        <Input
                                          type="number"
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
                                  name={`mainTrainingExercises.${index}.duration`}
                                  render={({ field }) => (
                                    <FormItem>
                                      <FormLabel>Duration (min)</FormLabel>
                                      <FormControl>
                                        <Input
                                          type="number"
                                          {...field}
                                          onChange={(e) => field.onChange(e.target.valueAsNumber)}
                                        />
                                      </FormControl>
                                      <FormMessage />
                                    </FormItem>
                                  )}
                                />
                              </div>
                              
                              <FormField
                                control={form.control}
                                name={`mainTrainingExercises.${index}.notes`}
                                render={({ field }) => (
                                  <FormItem>
                                    <FormLabel>Notes</FormLabel>
                                    <FormControl>
                                      <Textarea placeholder="Exercise details, technique tips, etc." {...field} />
                                    </FormControl>
                                    <FormMessage />
                                  </FormItem>
                                )}
                              />
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>
                  </CardContent>
                  
                  <CardFooter className="flex justify-between">
                    <Button variant="outline" type="button" onClick={() => setCurrentTab("warmup")}>
                      Previous
                    </Button>
                    <Button type="button" onClick={() => setCurrentTab("cooldown")}>
                      Next
                    </Button>
                  </CardFooter>
                </TabsContent>
                
                {/* Cooling Down */}
                <TabsContent value="cooldown">
                  <CardHeader>
                    <CardTitle>Cooling Down</CardTitle>
                    <CardDescription>
                      Define the cool-down phase of the training session.
                    </CardDescription>
                  </CardHeader>
                  
                  <CardContent className="space-y-4">
                    <FormField
                      control={form.control}
                      name="coolingDownDuration"
                      render={({ field }) => (
                        <FormItem>
                          <FormLabel>Duration (minutes): {field.value}</FormLabel>
                          <FormControl>
                            <Slider
                              min={5}
                              max={30}
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
                      name="coolingDownNotes"
                      render={({ field }) => (
                        <FormItem>
                          <FormLabel>Cool-down Description</FormLabel>
                          <FormControl>
                            <Textarea
                              placeholder="Describe the cool-down activities, recovery exercises, and stretches..."
                              className="min-h-[150px]"
                              {...field}
                            />
                          </FormControl>
                          <FormMessage />
                        </FormItem>
                      )}
                    />
                    
                    <Separator className="my-6" />
                    
                    <FormField
                      control={form.control}
                      name="notes"
                      render={({ field }) => (
                        <FormItem>
                          <FormLabel>Additional Notes</FormLabel>
                          <FormControl>
                            <Textarea
                              placeholder="Any additional notes, reminders, or instructions for the entire session..."
                              className="min-h-[100px]"
                              {...field}
                            />
                          </FormControl>
                          <FormMessage />
                        </FormItem>
                      )}
                    />
                  </CardContent>
                  
                  <CardFooter className="flex justify-between">
                    <Button variant="outline" type="button" onClick={() => setCurrentTab("main")}>
                      Previous
                    </Button>
                    <Button type="submit">Create Session</Button>
                  </CardFooter>
                </TabsContent>
              </form>
            </Form>
          </Card>
        </div>
      </Tabs>
    </div>
  );
} 