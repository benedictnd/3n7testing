import { useState, useMemo } from 'react';
import { useApiClient, ReportFormat } from '../lib/api-client';
import Head from 'next/head';
import { useRouter } from 'next/router';
import {
  TrainingReportData,
  AttendanceReportData,
  FeedbackReportData,
  ReportFormValues,
  TrainingSessionSummary,
  SessionAttendance,
  AttendanceAthleteSummary,
  FeedbackDetail,
  SessionFeedbackSummary,
  MonthlyReportData,
  IndependentTrainingSummary
} from '../lib/types/report';
import { format } from 'date-fns';

// Import UI components
import {
  Button,
  DatePicker,
  Form,
  Layout,
  Menu,
  message,
  Select,
  Tabs,
  Typography,
  Card as AntCard
} from 'antd';

// Import shadcn/ui components
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Calendar } from '@/components/ui/calendar';

const { Title, Text } = Typography;
const { Content, Sider } = Layout;
const { Option } = Select;
const { TabPane } = Tabs;

// Define date utility functions
const formatDate = (date: Date) => {
  return date.toISOString().split('T')[0];
};

type ReportType = 'training' | 'attendance' | 'feedback' | 'monthly';
type ReportData = TrainingReportData | AttendanceReportData | FeedbackReportData | MonthlyReportData | null;

const ReportsPage = () => {
  const apiClient = useApiClient();
  const router = useRouter();
  const [selectedTab, setSelectedTab] = useState<ReportType>('training');
  const [loading, setLoading] = useState<boolean>(false);
  const [reportData, setReportData] = useState<ReportData>(null);
  
  const [form] = Form.useForm();

  // Handle form submission
  const handleSubmit = async (values: ReportFormValues) => {
    setLoading(true);
    
    try {
      // Safely access date values
      if (!values.dateRange || !Array.isArray(values.dateRange) || values.dateRange.length < 2) {
        message.error('Please select a valid date range');
        setLoading(false);
        return;
      }
      
      const startDate = formatDate(values.dateRange[0]);
      const endDate = formatDate(values.dateRange[1]);
      const format = values.format || ReportFormat.JSON;
      
      let response;
      
      switch (selectedTab) {
        case 'training':
          response = await apiClient.getTrainingReport({
            startDate,
            endDate,
            format,
          });
          break;
          
        case 'attendance':
          response = await apiClient.getAttendanceReport({
            startDate,
            endDate,
            athleteId: values.athleteId,
            format,
          });
          break;
          
        case 'feedback':
          response = await apiClient.getFeedbackReport({
            startDate,
            endDate,
            sessionId: values.sessionId,
            format,
          });
          break;
          
        case 'monthly':
          response = await apiClient.getMonthlyReport({
            startDate,
            endDate,
            format,
          });
          break;
          
        default:
          message.error('Invalid report type');
          setLoading(false);
          return;
      }
      
      if (response.success && format === ReportFormat.JSON) {
        if (response.data) {
          setReportData(response.data);
          message.success('Report generated successfully');
        }
      } else if (response.success) {
        // For PDF and PPT, the API client handles the download
        message.success('Report downloaded successfully');
      } else {
        message.error(response.error || 'Failed to generate report');
      }
    } catch (error) {
      console.error('Error generating report:', error);
      message.error('An error occurred while generating the report');
    }
    
    setLoading(false);
  };

  // Render report based on selected tab
  const renderReport = () => {
    if (!reportData) return null;
    
    switch (selectedTab) {
      case 'training':
        const trainingReport = reportData as TrainingReportData;
        return (
          <AntCard title={trainingReport.title} style={{ marginTop: 20 }}>
            <div>
              <Text strong>Date Range:</Text> {trainingReport.date_range}
            </div>
            <div>
              <Text strong>Total Sessions:</Text> {trainingReport.summary.total_sessions}
            </div>
            <div>
              <Text strong>Total Attendees:</Text> {trainingReport.summary.total_attendees}
            </div>
            <div>
              <Text strong>Avg Attendees Per Session:</Text> {trainingReport.summary.avg_attendees_per_session}
            </div>
            
            <Title level={4} style={{ marginTop: 20 }}>Sessions</Title>
            {trainingReport.data.map((session: TrainingSessionSummary) => (
              <AntCard key={session.id} style={{ marginBottom: 10 }}>
                <div>
                  <Text strong>{session.date}</Text> - {session.type}
                </div>
                <div>Coach: {session.coach_name}</div>
                <div>Attendees: {session.attendees_count}</div>
                <div>Duration: {session.duration_minutes} minutes</div>
                <div>
                  <Text strong>Feedback:</Text> Quality {session.feedback.training_quality_avg}/5, 
                  Expectations {session.feedback.expectations_avg}/5
                </div>
              </AntCard>
            ))}
          </AntCard>
        );
        
      case 'attendance':
        const attendanceReport = reportData as AttendanceReportData;
        return (
          <AntCard title={attendanceReport.title} style={{ marginTop: 20 }}>
            <div>
              <Text strong>Date Range:</Text> {attendanceReport.date_range}
            </div>
            
            {/* Check if we have athlete-specific data */}
            {'attended_count' in attendanceReport.data[0] ? (
              <div>
                {/* Single athlete report */}
                {attendanceReport.data.map((athlete: any) => {
                  const athleteData = athlete as unknown as { 
                    athlete_name: string; 
                    attendance_rate: number;
                    attended_count: number;
                    total_count: number;
                    sessions: SessionAttendance[];
                  };
                  
                  return (
                    <div key={athleteData.athlete_name}>
                      <div>
                        <Text strong>Athlete:</Text> {athleteData.athlete_name}
                      </div>
                      <div>
                        <Text strong>Attendance Rate:</Text> {athleteData.attendance_rate}%
                      </div>
                      <div>
                        <Text strong>Sessions Attended:</Text> {athleteData.attended_count} of {athleteData.total_count}
                      </div>
                      
                      <Title level={4} style={{ marginTop: 20 }}>Sessions</Title>
                      {athleteData.sessions.map((session: SessionAttendance) => (
                        <AntCard key={session.id} style={{ marginBottom: 10 }}>
                          <div>
                            <Text strong>{session.date}</Text> - {session.type}
                          </div>
                          <div>Coach: {session.coach_name}</div>
                          <div>Status: {session.attended 
                            ? `Attended (Checked in at ${session.check_in_time})` 
                            : 'Missed'}
                          </div>
                        </AntCard>
                      ))}
                    </div>
                  );
                })}
              </div>
            ) : (
              <div>
                {/* Team attendance report */}
                <div>
                  <Text strong>Total Athletes:</Text> {attendanceReport.summary.total_athletes}
                </div>
                <div>
                  <Text strong>Average Attendance Rate:</Text> {attendanceReport.summary.avg_attendance_rate}%
                </div>
                
                <Title level={4} style={{ marginTop: 20 }}>Athletes</Title>
                {attendanceReport.data.flatMap((teamData: any) => {
                  // Ensure we have the correct structure for team data
                  if (!teamData.athletes) return [];
                  
                  return teamData.athletes.map((athlete: AttendanceAthleteSummary) => (
                    <AntCard key={athlete.athlete_id} style={{ marginBottom: 10 }}>
                      <div>
                        <Text strong>{athlete.athlete_name}</Text>
                      </div>
                      <div>Attendance Rate: {athlete.attendance_rate}%</div>
                      <div>Sessions Attended: {athlete.sessions_attended} of {athlete.sessions_attended + athlete.sessions_missed}</div>
                    </AntCard>
                  ));
                })}
              </div>
            )}
          </AntCard>
        );
        
      case 'feedback':
        const feedbackReport = reportData as FeedbackReportData;
        return (
          <AntCard title={feedbackReport.title} style={{ marginTop: 20 }}>
            <div>
              <Text strong>Date Range:</Text> {feedbackReport.date_range}
            </div>
            
            <div>
              <Text strong>Total Feedback:</Text> {
                feedbackReport.summary.total_feedback !== undefined 
                  ? feedbackReport.summary.total_feedback 
                  : feedbackReport.summary.feedback_count
              }
            </div>
            <div>
              <Text strong>Avg Training Quality:</Text> {
                feedbackReport.summary.avg_training_quality !== undefined 
                  ? feedbackReport.summary.avg_training_quality 
                  : feedbackReport.summary.training_quality_avg
              }/5
            </div>
            <div>
              <Text strong>Avg Expectations Met:</Text> {
                feedbackReport.summary.avg_expectations !== undefined 
                  ? feedbackReport.summary.avg_expectations 
                  : feedbackReport.summary.expectations_avg
              }/5
            </div>
            
            {/* Check if we have session feedback summaries */}
            {'session_id' in feedbackReport.data[0] ? (
              <div>
                <Title level={4} style={{ marginTop: 20 }}>Sessions</Title>
                {feedbackReport.data.map((item: any) => {
                  const session = item as SessionFeedbackSummary;
                  return (
                    <AntCard key={session.session_id} style={{ marginBottom: 10 }}>
                      <div>
                        <Text strong>{session.date}</Text> - {session.type}
                      </div>
                      <div>Coach: {session.coach_name}</div>
                      <div>Feedback Count: {session.feedback_count}</div>
                      <div>Training Quality: {session.training_quality_avg}/5</div>
                      <div>Expectations: {session.expectations_avg}/5</div>
                    </AntCard>
                  );
                })}
              </div>
            ) : (
              <div>
                <Title level={4} style={{ marginTop: 20 }}>Feedback</Title>
                {feedbackReport.data.map((item: any) => {
                  const feedback = item as FeedbackDetail;
                  return (
                    <AntCard key={feedback.id} style={{ marginBottom: 10 }}>
                      <div>
                        <Text strong>{feedback.athlete_name}</Text> - {feedback.created_at}
                      </div>
                      <div>Training Quality: {feedback.training_quality}/5</div>
                      <div>Expectations: {feedback.expectations}/5</div>
                      <div>Body Condition: {feedback.body_condition}/5</div>
                      <div>Intensity: {feedback.intensity}/5</div>
                      {feedback.notes && <div>Notes: {feedback.notes}</div>}
                    </AntCard>
                  );
                })}
              </div>
            )}
          </AntCard>
        );
        
      case 'monthly':
        const monthlyReport = reportData as MonthlyReportData;
        return (
          <MonthlyReport data={monthlyReport} />
        );
        
      default:
        return null;
    }
  };

  return (
    <Layout style={{ minHeight: '100vh' }}>
      <Head>
        <title>Reports - 3&7 Training Platform</title>
      </Head>
      
      <Sider width={200} theme="light">
        <Menu
          mode="inline"
          defaultSelectedKeys={['reports']}
          style={{ height: '100%', borderRight: 0 }}
        >
          <Menu.Item key="dashboard" onClick={() => router.push('/dashboard')}>
            Dashboard
          </Menu.Item>
          <Menu.Item key="sessions" onClick={() => router.push('/sessions')}>
            Training Sessions
          </Menu.Item>
          <Menu.Item key="reports" onClick={() => router.push('/reports')}>
            Reports
          </Menu.Item>
          <Menu.Item key="profile" onClick={() => router.push('/profile')}>
            My Profile
          </Menu.Item>
        </Menu>
      </Sider>
      
      <Layout style={{ padding: '0 24px 24px' }}>
        <Content style={{ padding: 24, margin: 0, minHeight: 280 }}>
          <Title level={2}>Reports</Title>
          
          <Tabs activeKey={selectedTab} onChange={(key: string) => setSelectedTab(key as ReportType)}>
            <TabPane tab="Training Reports" key="training">
              <Form
                form={form}
                layout="vertical"
                onFinish={handleSubmit}
                initialValues={{
                  format: ReportFormat.JSON,
                }}
              >
                <Form.Item
                  name="dateRange"
                  label="Date Range"
                  rules={[{ required: true, message: 'Please select a date range' }]}
                >
                  <DatePicker.RangePicker style={{ width: '100%' }} />
                </Form.Item>
                
                <Form.Item
                  name="format"
                  label="Format"
                >
                  <Select>
                    <Option value={ReportFormat.JSON}>View on Screen</Option>
                    <Option value={ReportFormat.PDF}>Download as PDF</Option>
                    <Option value={ReportFormat.PPT}>Download as PowerPoint</Option>
                  </Select>
                </Form.Item>
                
                <Form.Item>
                  <Button type="primary" htmlType="submit" loading={loading}>
                    Generate Report
                  </Button>
                </Form.Item>
              </Form>
            </TabPane>
            
            <TabPane tab="Attendance Reports" key="attendance">
              <Form
                form={form}
                layout="vertical"
                onFinish={handleSubmit}
                initialValues={{
                  format: ReportFormat.JSON,
                }}
              >
                <Form.Item
                  name="dateRange"
                  label="Date Range"
                  rules={[{ required: true, message: 'Please select a date range' }]}
                >
                  <DatePicker.RangePicker style={{ width: '100%' }} />
                </Form.Item>
                
                <Form.Item
                  name="athleteId"
                  label="Athlete (Optional)"
                >
                  <Select allowClear placeholder="Select an athlete for individual report">
                    <Option value="athlete-1">John Doe</Option>
                    <Option value="athlete-2">Jane Smith</Option>
                    <Option value="athlete-3">Sam Johnson</Option>
                  </Select>
                </Form.Item>
                
                <Form.Item
                  name="format"
                  label="Format"
                >
                  <Select>
                    <Option value={ReportFormat.JSON}>View on Screen</Option>
                    <Option value={ReportFormat.PDF}>Download as PDF</Option>
                    <Option value={ReportFormat.PPT}>Download as PowerPoint</Option>
                  </Select>
                </Form.Item>
                
                <Form.Item>
                  <Button type="primary" htmlType="submit" loading={loading}>
                    Generate Report
                  </Button>
                </Form.Item>
              </Form>
            </TabPane>
            
            <TabPane tab="Feedback Reports" key="feedback">
              <Form
                form={form}
                layout="vertical"
                onFinish={handleSubmit}
                initialValues={{
                  format: ReportFormat.JSON,
                }}
              >
                <Form.Item
                  name="dateRange"
                  label="Date Range"
                  rules={[{ required: true, message: 'Please select a date range' }]}
                >
                  <DatePicker.RangePicker style={{ width: '100%' }} />
                </Form.Item>
                
                <Form.Item
                  name="sessionId"
                  label="Session (Optional)"
                >
                  <Select allowClear placeholder="Select a session for detailed feedback">
                    <Option value="session-1">Strength Training - 2023-09-15</Option>
                    <Option value="session-2">Recovery Session - 2023-09-18</Option>
                    <Option value="session-3">Team Practice - 2023-09-20</Option>
                  </Select>
                </Form.Item>
                
                <Form.Item
                  name="format"
                  label="Format"
                >
                  <Select>
                    <Option value={ReportFormat.JSON}>View on Screen</Option>
                    <Option value={ReportFormat.PDF}>Download as PDF</Option>
                    <Option value={ReportFormat.PPT}>Download as PowerPoint</Option>
                  </Select>
                </Form.Item>
                
                <Form.Item>
                  <Button type="primary" htmlType="submit" loading={loading}>
                    Generate Report
                  </Button>
                </Form.Item>
              </Form>
            </TabPane>
            
            <TabPane tab="Monthly Reports" key="monthly">
              <Form
                form={form}
                layout="vertical"
                onFinish={handleSubmit}
                initialValues={{
                  format: ReportFormat.JSON,
                }}
              >
                <Form.Item
                  name="dateRange"
                  label="Date Range"
                  rules={[{ required: true, message: 'Please select a date range' }]}
                >
                  <DatePicker.RangePicker style={{ width: '100%' }} />
                </Form.Item>
                
                <Form.Item
                  name="format"
                  label="Format"
                >
                  <Select>
                    <Option value={ReportFormat.JSON}>View on Screen</Option>
                    <Option value={ReportFormat.PDF}>Download as PDF</Option>
                    <Option value={ReportFormat.PPT}>Download as PowerPoint</Option>
                  </Select>
                </Form.Item>
                
                <Form.Item>
                  <Button type="primary" htmlType="submit" loading={loading}>
                    Generate Report
                  </Button>
                </Form.Item>
              </Form>
            </TabPane>
          </Tabs>
          
          {renderReport()}
        </Content>
      </Layout>
    </Layout>
  );
};

const MonthlyReport = ({ data }: { data: MonthlyReportData }) => {
  const [selectedMonth, setSelectedMonth] = useState<Date>(new Date());
  
  // Safely extract and format data with fallbacks for summary metrics
  const summary = {
    totalSessions: data.summary?.total_sessions ?? 0,
    totalAttendees: data.summary?.total_attendees ?? 0,
    avgAttendeesPerSession: data.summary?.avg_attendees_per_session ?? 0,
    independentTrainingCount: data.summary?.independent_training_count ?? 0,
    trainingTypes: data.summary?.independent_training_types ?? {}
  };

  // Group sessions by week with proper null/undefined checks
  const sessionsByWeek = useMemo(() => {
    const weeks: Record<number, TrainingSessionSummary[]> = {};
    
    if (Array.isArray(data.data)) {
      data.data.forEach(session => {
        if (session && session.date) {
          const sessionDate = new Date(session.date);
          // Check if the date is valid
          if (!isNaN(sessionDate.getTime())) {
            const firstDay = new Date(sessionDate.getFullYear(), sessionDate.getMonth(), 1);
            const weekNumber = Math.ceil((sessionDate.getDate() + firstDay.getDay()) / 7);
            
            if (!weeks[weekNumber]) {
              weeks[weekNumber] = [];
            }
            weeks[weekNumber].push(session);
          }
        }
      });
    }
    
    return weeks;
  }, [data.data]);

  // Group independent training by week with proper null/undefined checks
  const independentTrainingByWeek = useMemo(() => {
    const weeks: Record<number, IndependentTrainingSummary[]> = {};
    
    if (Array.isArray(data.independent_training)) {
      data.independent_training.forEach(training => {
        if (training && training.date) {
          const trainingDate = new Date(training.date);
          // Check if the date is valid
          if (!isNaN(trainingDate.getTime())) {
            const firstDay = new Date(trainingDate.getFullYear(), trainingDate.getMonth(), 1);
            const weekNumber = Math.ceil((trainingDate.getDate() + firstDay.getDay()) / 7);
            
            if (!weeks[weekNumber]) {
              weeks[weekNumber] = [];
            }
            weeks[weekNumber].push(training);
          }
        }
      });
    }
    
    return weeks;
  }, [data.independent_training]);

  // Calculate how many weeks to display (default to 4)
  const weeksInMonth = useMemo(() => {
    const uniqueWeeks = new Set([
      ...Object.keys(sessionsByWeek).map(Number),
      ...Object.keys(independentTrainingByWeek).map(Number)
    ]);
    return uniqueWeeks.size > 0 ? Math.max(...uniqueWeeks) : 4;
  }, [sessionsByWeek, independentTrainingByWeek]);

  // Format date safely with fallback
  const formatDateSafely = (dateString: string, formatString: string): string => {
    try {
      const date = new Date(dateString);
      if (isNaN(date.getTime())) {
        return 'Invalid date';
      }
      return format(date, formatString);
    } catch (error) {
      console.error(`Error formatting date: ${dateString}`, error);
      return 'Invalid date';
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h2 className="text-2xl font-bold">Monthly Report</h2>
        <div className="flex gap-4">
          <Calendar
            mode="single"
            selected={selectedMonth}
            onSelect={(date) => date && setSelectedMonth(date)}
            className="rounded-md border"
          />
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <Card>
          <CardHeader>
            <CardTitle className="text-sm font-medium">Total Sessions</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{summary.totalSessions}</div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader>
            <CardTitle className="text-sm font-medium">Total Attendees</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{summary.totalAttendees}</div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader>
            <CardTitle className="text-sm font-medium">Avg. Attendees/Session</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{summary.avgAttendeesPerSession.toFixed(1)}</div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader>
            <CardTitle className="text-sm font-medium">Independent Training</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{summary.independentTrainingCount}</div>
          </CardContent>
        </Card>
      </div>

      <div className="space-y-4">
        <h3 className="text-lg font-semibold">Weekly Breakdown</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          {Array.from({ length: weeksInMonth }, (_, i) => i + 1).map(week => (
            <Card key={week}>
              <CardHeader>
                <CardTitle className="text-sm font-medium">Week {week}</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div>
                    <h4 className="text-sm font-medium mb-2">Group Sessions</h4>
                    {sessionsByWeek[week] && sessionsByWeek[week].length > 0 ? (
                      <ul className="space-y-2">
                        {sessionsByWeek[week].map(session => (
                          <li key={session.id} className="text-sm">
                            <div className="font-medium">{session.title || 'Unnamed Session'}</div>
                            <div className="text-muted-foreground">
                              {formatDateSafely(session.date, 'MMM d')} - {Array.isArray(session.attendees) ? session.attendees.length : 0} attendees
                            </div>
                          </li>
                        ))}
                      </ul>
                    ) : (
                      <p className="text-sm text-muted-foreground">No group sessions this week</p>
                    )}
                  </div>
                  <div>
                    <h4 className="text-sm font-medium mb-2">Independent Training</h4>
                    {independentTrainingByWeek[week] && independentTrainingByWeek[week].length > 0 ? (
                      <ul className="space-y-2">
                        {independentTrainingByWeek[week].map(training => (
                          <li key={training.id} className="text-sm">
                            <div className="font-medium">
                              {typeof training.type === 'string' ? training.type.replace(/_/g, ' ') : 'Unknown Type'}
                            </div>
                            <div className="text-muted-foreground">
                              {formatDateSafely(training.date, 'MMM d')} - {formatDateSafely(training.start_time, 'h:mm a')}
                            </div>
                            <div className="text-xs text-muted-foreground">
                              {training.location || 'No location'} - Intensity: {training.intensity}/10
                            </div>
                          </li>
                        ))}
                      </ul>
                    ) : (
                      <p className="text-sm text-muted-foreground">No independent training this week</p>
                    )}
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      </div>

      <div className="space-y-4">
        <h3 className="text-lg font-semibold">Independent Training Types</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {Object.entries(summary.trainingTypes).length > 0 ? (
            Object.entries(summary.trainingTypes).map(([type, count]) => (
              <Card key={type}>
                <CardHeader>
                  <CardTitle className="text-sm font-medium capitalize">
                    {typeof type === 'string' ? type.replace(/_/g, ' ') : 'Unknown Type'}
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">{typeof count === 'number' ? count : 0}</div>
                </CardContent>
              </Card>
            ))
          ) : (
            <div className="col-span-3">
              <p className="text-center text-muted-foreground">No independent training data available</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default ReportsPage; 