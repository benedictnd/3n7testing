export type Database = {
  public: {
    Tables: {
      users: {
        Row: {
          id: string;
          email: string;
          created_at: string;
          updated_at: string;
          full_name: string | null;
          role: 'admin' | 'user' | 'client';
          mfa_enabled: boolean;
        };
        Insert: {
          id?: string;
          email: string;
          created_at?: string;
          updated_at?: string;
          full_name?: string | null;
          role?: 'admin' | 'user' | 'client';
          mfa_enabled?: boolean;
        };
        Update: {
          id?: string;
          email?: string;
          created_at?: string;
          updated_at?: string;
          full_name?: string | null;
          role?: 'admin' | 'user' | 'client';
          mfa_enabled?: boolean;
        };
      };
      projects: {
        Row: {
          id: string;
          name: string;
          description: string | null;
          client_id: string;
          created_at: string;
          updated_at: string;
          created_by: string;
          status: 'active' | 'completed' | 'on-hold';
        };
        Insert: {
          id?: string;
          name: string;
          description?: string | null;
          client_id: string;
          created_at?: string;
          updated_at?: string;
          created_by: string;
          status?: 'active' | 'completed' | 'on-hold';
        };
        Update: {
          id?: string;
          name?: string;
          description?: string | null;
          client_id?: string;
          created_at?: string;
          updated_at?: string;
          created_by?: string;
          status?: 'active' | 'completed' | 'on-hold';
        };
      };
      clients: {
        Row: {
          id: string;
          name: string;
          email: string;
          phone: string | null;
          created_at: string;
          updated_at: string;
        };
        Insert: {
          id?: string;
          name: string;
          email: string;
          phone?: string | null;
          created_at?: string;
          updated_at?: string;
        };
        Update: {
          id?: string;
          name?: string;
          email?: string;
          phone?: string | null;
          created_at?: string;
          updated_at?: string;
        };
      };
      tasks: {
        Row: {
          id: string;
          title: string;
          description: string | null;
          project_id: string;
          assigned_to: string | null;
          created_at: string;
          updated_at: string;
          due_date: string | null;
          status: 'pending' | 'in-progress' | 'completed';
          priority: 'low' | 'medium' | 'high';
        };
        Insert: {
          id?: string;
          title: string;
          description?: string | null;
          project_id: string;
          assigned_to?: string | null;
          created_at?: string;
          updated_at?: string;
          due_date?: string | null;
          status?: 'pending' | 'in-progress' | 'completed';
          priority?: 'low' | 'medium' | 'high';
        };
        Update: {
          id?: string;
          title?: string;
          description?: string | null;
          project_id?: string;
          assigned_to?: string | null;
          created_at?: string;
          updated_at?: string;
          due_date?: string | null;
          status?: 'pending' | 'in-progress' | 'completed';
          priority?: 'low' | 'medium' | 'high';
        };
      };
      invoices: {
        Row: {
          id: string;
          client_id: string;
          project_id: string;
          amount: number;
          status: 'draft' | 'sent' | 'paid' | 'overdue';
          due_date: string;
          issued_date: string;
          created_at: string;
          updated_at: string;
        };
        Insert: {
          id?: string;
          client_id: string;
          project_id: string;
          amount: number;
          status?: 'draft' | 'sent' | 'paid' | 'overdue';
          due_date: string;
          issued_date: string;
          created_at?: string;
          updated_at?: string;
        };
        Update: {
          id?: string;
          client_id?: string;
          project_id?: string;
          amount?: number;
          status?: 'draft' | 'sent' | 'paid' | 'overdue';
          due_date?: string;
          issued_date?: string;
          created_at?: string;
          updated_at?: string;
        };
      };
    };
  };
}; 