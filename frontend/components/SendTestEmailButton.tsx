"use client";

import { useState } from "react";
import { Button } from "@/components/ui/button";
import { useToast } from "@/components/ui/toast";
import { useApiClient } from "@/lib/api-client";

export default function SendTestEmailButton() {
  const [isLoading, setIsLoading] = useState(false);
  const { toast } = useToast();
  const apiClient = useApiClient();

  const handleSendTestEmail = async () => {
    setIsLoading(true);
    try {
      const response = await apiClient.sendTestEmail();
      if (response.success) {
        toast({
          title: "Success",
          description: "Test email sent successfully!",
          variant: "default",
        });
      } else {
        toast({
          title: "Error",
          description: response.error || "Failed to send test email",
          variant: "destructive",
        });
      }
    } catch (error) {
      toast({
        title: "Error",
        description: "An unexpected error occurred while sending the test email",
        variant: "destructive",
      });
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <Button 
      variant="default" 
      onClick={handleSendTestEmail}
      disabled={isLoading}
      className="w-full sm:w-auto"
    >
      {isLoading ? 'Sending...' : 'Send Test Email'}
    </Button>
  );
} 