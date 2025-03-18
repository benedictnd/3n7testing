import { NextResponse } from 'next/server';
import { getServiceSupabase } from '@/lib/supabase';

export async function POST(request: Request) {
  // This is a protected route that should only be used during initial setup
  // Ideally it should be protected by an admin-only middleware
  
  try {
    // Get the Supabase client with admin privileges
    const adminSupabase = getServiceSupabase();
    
    // Create the dummy user without hardcoding the password
    const { data, error } = await adminSupabase.auth.admin.createUser({
      email: 'dev@threenseven.or.id',
      password: process.env.INITIAL_ADMIN_PASSWORD, // Set this in your env vars
      email_confirm: true, // Auto-confirm the email
      user_metadata: {
        full_name: 'Development Admin',
        role: 'admin',
      },
      app_metadata: {
        role: 'admin',
      },
    });
    
    if (error) {
      console.error('Error creating user:', error);
      return NextResponse.json(
        { error: 'Failed to create user: ' + error.message },
        { status: 500 }
      );
    }
    
    // Insert additional user data in the users table using PostgreSQL
    const { error: insertError } = await adminSupabase
      .from('users')
      .insert({
        id: data.user.id,
        email: data.user.email,
        full_name: 'Development Admin',
        role: 'admin',
        mfa_enabled: false,
      });
    
    if (insertError) {
      console.error('Error inserting user data:', insertError);
      return NextResponse.json(
        { error: 'Failed to insert user data: ' + insertError.message },
        { status: 500 }
      );
    }
    
    return NextResponse.json(
      { 
        success: true, 
        message: 'Initial user created successfully',
        userId: data.user.id,
      },
      { status: 201 }
    );
    
  } catch (error) {
    console.error('Unexpected error creating user:', error);
    return NextResponse.json(
      { error: 'An unexpected error occurred' },
      { status: 500 }
    );
  }
} 