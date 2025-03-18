import { test, expect, Page } from '@playwright/test';
import { format, addDays } from 'date-fns';

// Mock data for testing
const ATHLETE = {
  email: 'athlete@example.com',
  password: 'password123',
  name: 'Michael Johnson'
};

const COACH = {
  email: 'coach@example.com',
  password: 'password123',
  name: 'Coach Smith'
};

// Equipment list for testing
const mockEquipment = [
  { name: 'Swim Goggles', category: 'Swimming', totalCount: 10, availableCount: 8 },
  { name: 'Kickboard', category: 'Swimming', totalCount: 15, availableCount: 12 },
  { name: 'Cycling Helmet', category: 'Cycling', totalCount: 5, availableCount: 3 },
  { name: 'Training Bike', category: 'Cycling', totalCount: 4, availableCount: 2 },
  { name: 'Resistance Bands', category: 'General', totalCount: 20, availableCount: 15 }
];

// Test helpers
async function loginAs(page: Page, user: { email: string, password: string }) {
  await page.goto('/login');
  await page.fill('input[name="email"]', user.email);
  await page.fill('input[name="password"]', user.password);
  await page.click('button[type="submit"]');
  await page.waitForURL('/dashboard');
}

async function createIndependentTraining(page: Page, options: {
  title: string;
  type: string;
  date?: string;
  location: string;
  equipment?: string[];
  intensity?: number;
  bodyCondition?: number;
}) {
  // Go to independent training page
  await page.goto('/independent-training');
  
  // Click on "Log New Training" button
  await page.click('button:text("Log New Training")');
  
  // Fill the form
  await page.fill('input#title', options.title);
  await page.click('div[role="combobox"]'); // Open select dropdown
  await page.click(`div[role="option"]:text-is("${options.type}")`);
  
  if (options.date) {
    await page.fill('input#date', options.date);
  }
  
  await page.fill('input#location', options.location);
  
  // Set default times if not specified
  await page.fill('input#start_time', '09:00');
  await page.fill('input#end_time', '10:30');
  
  // Add equipment if specified
  if (options.equipment && options.equipment.length > 0) {
    await page.fill('input#equipment_needed', options.equipment.join(', '));
  }
  
  // Set intensity if specified
  if (options.intensity) {
    // This is a simplified approach - actual implementation depends on the slider component
    await page.evaluate((intensity) => {
      const slider = document.querySelector('.intensity-slider');
      if (slider) (slider as any).value = intensity;
    }, options.intensity);
  }
  
  // Set body condition if specified
  if (options.bodyCondition) {
    // This is a simplified approach - actual implementation depends on the slider component
    await page.evaluate((condition) => {
      const slider = document.querySelector('.body-condition-slider');
      if (slider) (slider as any).value = condition;
    }, options.bodyCondition);
  }
  
  // Submit the form
  await page.click('button:text("Save Training Session")');
  
  // Wait for form to be submitted successfully
  await page.waitForSelector('text=Log New Training', { state: 'visible' });
}

test.describe('Integrated Training System Tests', () => {
  // Setup for each test
  test.beforeEach(async ({ page }) => {
    // Navigate to login page
    await page.goto('/login');
  });

  test('AUTH-01: Valid user login with athlete account', async ({ page }) => {
    // Fill login form
    await page.fill('[data-testid="email-input"]', ATHLETE.email);
    await page.fill('[data-testid="password-input"]', ATHLETE.password);
    await page.click('[data-testid="login-button"]');

    // Verify redirect to dashboard
    await expect(page).toHaveURL('/dashboard');
    
    // Verify athlete name appears on dashboard
    await expect(page.locator('[data-testid="user-greeting"]')).toContainText(ATHLETE.name);
  });

  test('IND-01: Create independent training session with equipment', async ({ page }) => {
    // Login as athlete
    await page.fill('[data-testid="email-input"]', ATHLETE.email);
    await page.fill('[data-testid="password-input"]', ATHLETE.password);
    await page.click('[data-testid="login-button"]');
    
    // Navigate to independent training page
    await page.click('[data-testid="nav-independent-training"]');
    await expect(page).toHaveURL('/independent-training');
    
    // Click on create new session button
    await page.click('[data-testid="create-training-button"]');
    
    // Fill out the training form
    const tomorrow = new Date();
    tomorrow.setDate(tomorrow.getDate() + 1);
    const formattedDate = format(tomorrow, 'yyyy-MM-dd');
    
    await page.fill('[data-testid="title-input"]', 'Test Swimming Session');
    await page.selectOption('[data-testid="type-select"]', 'SKILLS');
    await page.fill('[data-testid="date-input"]', formattedDate);
    await page.fill('[data-testid="start-time-input"]', '09:00');
    await page.fill('[data-testid="end-time-input"]', '10:30');
    await page.fill('[data-testid="location-input"]', 'Local Pool');
    await page.fill('[data-testid="description-input"]', 'Technique practice for freestyle');
    
    // Select equipment
    await page.click('[data-testid="add-equipment-button"]');
    await page.selectOption('[data-testid="equipment-select"]', 'Swim Goggles');
    await page.fill('[data-testid="equipment-quantity"]', '1');
    await page.click('[data-testid="add-equipment-confirm"]');
    
    await page.click('[data-testid="add-equipment-button"]');
    await page.selectOption('[data-testid="equipment-select"]', 'Kickboard');
    await page.fill('[data-testid="equipment-quantity"]', '1');
    await page.click('[data-testid="add-equipment-confirm"]');
    
    // Set intensity and body condition
    await page.selectOption('[data-testid="intensity-select"]', 'MEDIUM');
    await page.selectOption('[data-testid="body-condition-select"]', 'GOOD');
    
    // Submit the form
    await page.click('[data-testid="submit-training"]');
    
    // Verify success message
    await expect(page.locator('[data-testid="success-message"]')).toBeVisible();
    await expect(page.locator('[data-testid="success-message"]')).toContainText('Training session created successfully');
    
    // Verify session appears in the list
    await expect(page.locator('[data-testid="session-card"]')).toContainText('Test Swimming Session');
    await expect(page.locator('[data-testid="session-card"]')).toContainText('Local Pool');
    
    // Verify equipment is listed
    await expect(page.locator('[data-testid="session-equipment"]')).toContainText('Swim Goggles');
    await expect(page.locator('[data-testid="session-equipment"]')).toContainText('Kickboard');
  });

  test('CAL-01: View combined calendar with both group and independent sessions', async ({ page }) => {
    // Login as athlete
    await page.fill('[data-testid="email-input"]', ATHLETE.email);
    await page.fill('[data-testid="password-input"]', ATHLETE.password);
    await page.click('[data-testid="login-button"]');
    
    // Navigate to integrated training page
    await page.click('[data-testid="nav-integrated-training"]');
    await expect(page).toHaveURL('/integrated-training');
    
    // Verify calendar is visible
    await expect(page.locator('[data-testid="training-calendar"]')).toBeVisible();
    
    // Verify independent sessions are displayed
    await expect(page.locator('[data-testid="independent-session"]')).toBeVisible();
    
    // Verify group sessions are displayed (assuming there are mock group sessions)
    await expect(page.locator('[data-testid="group-session"]')).toBeVisible();
  });

  test('EQP-01: View equipment inventory with availability', async ({ page }) => {
    // Login as athlete
    await page.fill('[data-testid="email-input"]', ATHLETE.email);
    await page.fill('[data-testid="password-input"]', ATHLETE.password);
    await page.click('[data-testid="login-button"]');
    
    // Navigate to integrated training page
    await page.click('[data-testid="nav-integrated-training"]');
    
    // Click on equipment tab
    await page.click('[data-testid="equipment-tab"]');
    
    // Verify equipment list is visible
    await expect(page.locator('[data-testid="equipment-list"]')).toBeVisible();
    
    // Check for specific equipment items
    for (const equipment of mockEquipment) {
      await expect(page.locator(`[data-testid="equipment-item-${equipment.name.replace(/\s+/g, '-').toLowerCase()}"]`))
        .toContainText(equipment.name);
      await expect(page.locator(`[data-testid="equipment-item-${equipment.name.replace(/\s+/g, '-').toLowerCase()}"]`))
        .toContainText(`Available: ${equipment.availableCount}/${equipment.totalCount}`);
    }
  });

  test('EQP-02: Reserve equipment and verify inventory update', async ({ page }) => {
    // Login as athlete
    await page.fill('[data-testid="email-input"]', ATHLETE.email);
    await page.fill('[data-testid="password-input"]', ATHLETE.password);
    await page.click('[data-testid="login-button"]');
    
    // Navigate to independent training page
    await page.click('[data-testid="nav-independent-training"]');
    
    // Create a new session with equipment
    await page.click('[data-testid="create-training-button"]');
    
    // Fill basic session details
    const tomorrow = new Date();
    tomorrow.setDate(tomorrow.getDate() + 1);
    const formattedDate = format(tomorrow, 'yyyy-MM-dd');
    
    await page.fill('[data-testid="title-input"]', 'Cycling Session');
    await page.selectOption('[data-testid="type-select"]', 'CARDIO');
    await page.fill('[data-testid="date-input"]', formattedDate);
    await page.fill('[data-testid="start-time-input"]', '14:00');
    await page.fill('[data-testid="end-time-input"]', '16:00');
    
    // Select cycling equipment
    await page.click('[data-testid="add-equipment-button"]');
    await page.selectOption('[data-testid="equipment-select"]', 'Cycling Helmet');
    await page.fill('[data-testid="equipment-quantity"]', '1');
    await page.click('[data-testid="add-equipment-confirm"]');
    
    await page.click('[data-testid="add-equipment-button"]');
    await page.selectOption('[data-testid="equipment-select"]', 'Training Bike');
    await page.fill('[data-testid="equipment-quantity"]', '1');
    await page.click('[data-testid="add-equipment-confirm"]');
    
    // Submit the form
    await page.click('[data-testid="submit-training"]');
    
    // Navigate to integrated training to check equipment
    await page.click('[data-testid="nav-integrated-training"]');
    await page.click('[data-testid="equipment-tab"]');
    
    // Verify cycling helmet count decreased
    await expect(page.locator('[data-testid="equipment-item-cycling-helmet"]'))
      .toContainText('Available: 2/5'); // Was 3/5 before
    
    // Verify training bike count decreased
    await expect(page.locator('[data-testid="equipment-item-training-bike"]'))
      .toContainText('Available: 1/4'); // Was 2/4 before
  });

  test('MSA-01: Multi-sport athlete profile shows all sports', async ({ page }) => {
    // Login as athlete
    await page.fill('[data-testid="email-input"]', ATHLETE.email);
    await page.fill('[data-testid="password-input"]', ATHLETE.password);
    await page.click('[data-testid="login-button"]');
    
    // Navigate to profile page
    await page.click('[data-testid="nav-profile"]');
    
    // Verify multiple sports are displayed
    await expect(page.locator('[data-testid="athlete-sports"]')).toContainText('Swimming');
    await expect(page.locator('[data-testid="athlete-sports"]')).toContainText('Cycling');
  });

  test('MSR-01: Multi-sport athlete report shows sport distribution', async ({ page }) => {
    // Login as athlete
    await page.fill('[data-testid="email-input"]', ATHLETE.email);
    await page.fill('[data-testid="password-input"]', ATHLETE.password);
    await page.click('[data-testid="login-button"]');
    
    // Navigate to reports page
    await page.click('[data-testid="nav-reports"]');
    
    // Select monthly report
    await page.click('[data-testid="monthly-report-button"]');
    
    // Verify report generation
    await expect(page.locator('[data-testid="report-content"]')).toBeVisible();
    
    // Verify sport distribution is shown
    await expect(page.locator('[data-testid="sport-distribution-chart"]')).toBeVisible();
    
    // Verify both sports are represented
    await expect(page.locator('[data-testid="sport-swimming"]')).toBeVisible();
    await expect(page.locator('[data-testid="sport-cycling"]')).toBeVisible();
  });

  test('INT-01: Coach can view athlete\'s independent training', async ({ page }) => {
    // Login as coach
    await page.fill('[data-testid="email-input"]', COACH.email);
    await page.fill('[data-testid="password-input"]', COACH.password);
    await page.click('[data-testid="login-button"]');
    
    // Navigate to athletes page
    await page.click('[data-testid="nav-athletes"]');
    
    // Select the test athlete
    await page.click(`[data-testid="athlete-${ATHLETE.email.replace('@', '-at-')}"]`);
    
    // Verify athlete details page loaded
    await expect(page.locator('[data-testid="athlete-detail-name"]')).toContainText(ATHLETE.name);
    
    // Check for independent training sessions
    await expect(page.locator('[data-testid="athlete-independent-sessions"]')).toBeVisible();
    
    // Verify the previously created sessions are visible
    await expect(page.locator('[data-testid="session-item"]')).toContainText('Test Swimming Session');
    await expect(page.locator('[data-testid="session-item"]')).toContainText('Cycling Session');
  });

  test('INT-02: Coach provides feedback on independent training', async ({ page }) => {
    // Login as coach
    await page.fill('[data-testid="email-input"]', COACH.email);
    await page.fill('[data-testid="password-input"]', COACH.password);
    await page.click('[data-testid="login-button"]');
    
    // Navigate to athletes page
    await page.click('[data-testid="nav-athletes"]');
    
    // Select the test athlete
    await page.click(`[data-testid="athlete-${ATHLETE.email.replace('@', '-at-')}"]`);
    
    // Click on the swimming session
    await page.click('[data-testid="session-item"]:has-text("Test Swimming Session")');
    
    // Add feedback
    await page.fill('[data-testid="feedback-input"]', 'Great job on the technique practice! Next time, try focusing on your breathing pattern.');
    await page.click('[data-testid="submit-feedback"]');
    
    // Verify feedback saved
    await expect(page.locator('[data-testid="feedback-message"]')).toBeVisible();
    await expect(page.locator('[data-testid="feedback-message"]')).toContainText('Feedback submitted successfully');
    
    // Login as athlete to verify feedback is visible
    await page.goto('/login');
    await page.fill('[data-testid="email-input"]', ATHLETE.email);
    await page.fill('[data-testid="password-input"]', ATHLETE.password);
    await page.click('[data-testid="login-button"]');
    
    // Navigate to independent training
    await page.click('[data-testid="nav-independent-training"]');
    
    // Click on the swimming session
    await page.click('[data-testid="session-card"]:has-text("Test Swimming Session")');
    
    // Verify feedback is visible
    await expect(page.locator('[data-testid="coach-feedback"]')).toContainText('Great job on the technique practice');
  });

  test('EDGE-01: Concurrent equipment booking shows warning', async ({ page, browser }) => {
    // Login as first athlete
    await page.fill('[data-testid="email-input"]', ATHLETE.email);
    await page.fill('[data-testid="password-input"]', ATHLETE.password);
    await page.click('[data-testid="login-button"]');
    
    // Navigate to independent training page
    await page.click('[data-testid="nav-independent-training"]');
    await page.click('[data-testid="create-training-button"]');
    
    // Fill out session details
    const tomorrow = new Date();
    tomorrow.setDate(tomorrow.getDate() + 1);
    const formattedDate = format(tomorrow, 'yyyy-MM-dd');
    
    await page.fill('[data-testid="title-input"]', 'Last Available Bike Session');
    await page.selectOption('[data-testid="type-select"]', 'CARDIO');
    await page.fill('[data-testid="date-input"]', formattedDate);
    await page.fill('[data-testid="start-time-input"]', '10:00');
    await page.fill('[data-testid="end-time-input"]', '11:00');
    
    // Select last available training bike
    await page.click('[data-testid="add-equipment-button"]');
    await page.selectOption('[data-testid="equipment-select"]', 'Training Bike');
    await page.fill('[data-testid="equipment-quantity"]', '1');
    await page.click('[data-testid="add-equipment-confirm"]');
    
    // Open a new browser context for second athlete
    const secondContext = await browser.newContext();
    const secondPage = await secondContext.newPage();
    
    // Login as second athlete
    await secondPage.goto('/login');
    await secondPage.fill('[data-testid="email-input"]', 'second-athlete@example.com');
    await secondPage.fill('[data-testid="password-input"]', 'Password123!');
    await secondPage.click('[data-testid="login-button"]');
    
    // Navigate to independent training
    await secondPage.click('[data-testid="nav-independent-training"]');
    await secondPage.click('[data-testid="create-training-button"]');
    
    // Fill out similar session details
    await secondPage.fill('[data-testid="title-input"]', 'Competing Bike Session');
    await secondPage.selectOption('[data-testid="type-select"]', 'CARDIO');
    await secondPage.fill('[data-testid="date-input"]', formattedDate);
    await secondPage.fill('[data-testid="start-time-input"]', '10:30'); // Overlapping time
    await secondPage.fill('[data-testid="end-time-input"]', '11:30');
    
    // Submit first athlete's session
    await page.click('[data-testid="submit-training"]');
    await expect(page.locator('[data-testid="success-message"]')).toBeVisible();
    
    // Try to book the same equipment with second athlete
    await secondPage.click('[data-testid="add-equipment-button"]');
    await secondPage.selectOption('[data-testid="equipment-select"]', 'Training Bike');
    await secondPage.fill('[data-testid="equipment-quantity"]', '1');
    await secondPage.click('[data-testid="add-equipment-confirm"]');
    
    // Submit and check for warning
    await secondPage.click('[data-testid="submit-training"]');
    await expect(secondPage.locator('[data-testid="equipment-warning"]')).toBeVisible();
    await expect(secondPage.locator('[data-testid="equipment-warning"]')).toContainText('Limited availability');
    
    // Close second context
    await secondContext.close();
  });

  test('PERF-01: Calendar renders efficiently with many sessions', async ({ page }) => {
    // Login as athlete
    await page.fill('[data-testid="email-input"]', ATHLETE.email);
    await page.fill('[data-testid="password-input"]', ATHLETE.password);
    await page.click('[data-testid="login-button"]');
    
    // Navigate to integrated training
    await page.click('[data-testid="nav-integrated-training"]');
    
    // Set performance measurement
    const startTime = Date.now();
    
    // Set calendar to month view to load more sessions
    await page.click('[data-testid="month-view-button"]');
    
    // Wait for calendar to fully load
    await page.waitForSelector('[data-testid="calendar-loaded"]');
    
    // Calculate render time
    const renderTime = Date.now() - startTime;
    
    // Verify render time is acceptable (under 2 seconds)
    expect(renderTime).toBeLessThan(2000);
    
    // Verify calendar has loaded multiple sessions
    const sessionCount = await page.locator('[data-testid="calendar-event"]').count();
    expect(sessionCount).toBeGreaterThan(10);
  });
}); 