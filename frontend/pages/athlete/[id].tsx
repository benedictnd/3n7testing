import React, { useState, useEffect } from 'react';
import { useRouter } from 'next/router';
import Image from 'next/image';
import Head from 'next/head';
import { format } from 'date-fns';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Separator } from '@/components/ui/separator';
import { Button } from '@/components/ui/button';
import { 
  Facebook, Twitter, Instagram, Link as LinkIcon, ArrowLeft, 
  Calendar, MapPin, Medal, Trophy, TrendingUp, Info, 
  Share2, Download, Award, Flag
} from 'lucide-react';
import { mockAthletes, AthleteData } from '../../lib/mock-athlete-data';

export default function AthleteProfile() {
  const router = useRouter();
  const { id } = router.query;
  const [athlete, setAthlete] = useState<AthleteData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [activeTab, setActiveTab] = useState('info');
  const [selectedYear, setSelectedYear] = useState<number>(new Date().getFullYear());
  const [selectedEvent, setSelectedEvent] = useState<string>('');

  useEffect(() => {
    const fetchAthleteData = async () => {
      if (!id) return;
      
      try {
        setLoading(true);
        
        // In a real app, you'd fetch from your API:
        // const response = await API.getUser(id as string);
        
        // For demo purposes, we'll use mock data:
        const athleteData = mockAthletes[id as string];
        
        if (!athleteData) {
          throw new Error('Athlete not found');
        }
        
        setAthlete(athleteData);
        setSelectedEvent(athleteData.mainEvent);
      } catch (err) {
        console.error('Error fetching athlete data:', err);
        setError('Failed to load athlete profile. Please try again later.');
      } finally {
        setLoading(false);
      }
    };

    fetchAthleteData();
  }, [id]);

  const handleBack = () => {
    router.back();
  };

  const handleYearChange = (year: number) => {
    setSelectedYear(year);
  };

  const handleEventChange = (event: string) => {
    setSelectedEvent(event);
  };

  const renderMedalColor = (medal?: 'gold' | 'silver' | 'bronze') => {
    if (!medal) return null;
    
    const colorClasses = {
      gold: "bg-yellow-400",
      silver: "bg-gray-300",
      bronze: "bg-amber-600"
    };
    
    return (
      <div className={`w-3 h-3 rounded-full ${colorClasses[medal]} mr-2`}></div>
    );
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center min-h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-primary"></div>
      </div>
    );
  }

  if (error || !athlete) {
    return (
      <div className="container mx-auto px-4 py-8">
        <div className="bg-red-50 border border-red-200 text-red-700 p-4 rounded-md">
          {error || 'Athlete not found'}
        </div>
        <Button onClick={handleBack} variant="outline" className="mt-4">
          <ArrowLeft className="w-4 h-4 mr-2" /> Go Back
        </Button>
      </div>
    );
  }

  // Calculate age from date of birth
  const calculateAge = (dateOfBirth: string): number => {
    const today = new Date();
    const birthDate = new Date(dateOfBirth);
    let age = today.getFullYear() - birthDate.getFullYear();
    const monthDifference = today.getMonth() - birthDate.getMonth();
    
    if (monthDifference < 0 || (monthDifference === 0 && today.getDate() < birthDate.getDate())) {
      age--;
    }
    
    return age;
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <Head>
        <title>{athlete.name} | Athlete Profile | 3&7 Training Platform</title>
        <meta name="description" content={`Athlete profile for ${athlete.name} - ${athlete.mainEvent}`} />
      </Head>

      {/* Top navigation */}
      <div className="bg-white border-b">
        <div className="container mx-auto px-4 py-4 flex justify-between items-center">
          <Button variant="ghost" onClick={handleBack} className="pl-0">
            <ArrowLeft className="w-4 h-4 mr-2" /> Back to Athletes
          </Button>
          <div className="flex items-center space-x-2">
            <Button variant="ghost" size="sm">
              <Share2 className="w-4 h-4 mr-2" /> Share
            </Button>
            <Button variant="ghost" size="sm">
              <Download className="w-4 h-4 mr-2" /> Download
            </Button>
          </div>
        </div>
      </div>

      {/* Hero section - closely matching World Athletics */}
      <div className="bg-gradient-to-r from-blue-900 to-blue-700 text-white">
        <div className="container mx-auto px-4 py-8">
          <div className="flex flex-col md:flex-row gap-8">
            {/* Profile Image */}
            <div className="md:w-1/3 flex justify-center">
              <div className="relative w-64 h-80 bg-blue-800 rounded-md overflow-hidden">
                <Image 
                  src={athlete.profileImage || '/images/athlete-placeholder.jpg'} 
                  alt={athlete.name}
                  fill
                  style={{ objectFit: 'cover' }}
                  className="rounded-md"
                  priority
                />
              </div>
            </div>

            {/* Athlete Info */}
            <div className="md:w-2/3">
              <div className="flex items-center mb-2">
                <div className="mr-3 h-6 w-9 relative overflow-hidden">
                  <Flag className="w-5 h-5 text-red-500" />
                </div>
                <span className="text-sm font-medium">{athlete.country}</span>
              </div>

              <h1 className="text-4xl font-bold mb-2">{athlete.name}</h1>
              <p className="text-xl mb-4">{athlete.mainEvent}</p>
              
              <div className="text-sm text-blue-200 mb-6 flex flex-wrap gap-2">
                {athlete.otherEvents.map((event, index) => (
                  <span key={index} className="bg-blue-800 bg-opacity-50 px-2 py-1 rounded-full">
                    {event}
                  </span>
                ))}
              </div>

              <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
                <div className="bg-blue-800 bg-opacity-50 p-4 rounded-md">
                  <p className="text-sm text-blue-200">World Ranking</p>
                  <div className="flex items-center">
                    <Trophy className="w-5 h-5 text-yellow-400 mr-2" />
                    <span className="text-2xl font-bold">#{athlete.worldRanking}</span>
                  </div>
                </div>

                <div className="bg-blue-800 bg-opacity-50 p-4 rounded-md">
                  <p className="text-sm text-blue-200">Personal Best</p>
                  <div className="flex items-center">
                    <Medal className="w-5 h-5 text-yellow-400 mr-2" />
                    <span className="text-2xl font-bold">
                      {athlete.personalBests && athlete.personalBests.length > 0 
                        ? athlete.personalBests[0].mark 
                        : 'N/A'}
                    </span>
                  </div>
                </div>

                <div className="bg-blue-800 bg-opacity-50 p-4 rounded-md">
                  <p className="text-sm text-blue-200">Season Best {new Date().getFullYear()}</p>
                  <div className="flex items-center">
                    <TrendingUp className="w-5 h-5 text-yellow-400 mr-2" />
                    <span className="text-2xl font-bold">
                      {athlete.seasonBests && athlete.seasonBests.length > 0 
                        ? athlete.seasonBests[0].mark 
                        : 'N/A'}
                    </span>
                  </div>
                </div>
              </div>

              {/* Social Links */}
              <div className="flex space-x-2">
                {athlete.socialsLinks?.facebook && (
                  <a href={athlete.socialsLinks.facebook} target="_blank" rel="noopener noreferrer" 
                    className="bg-blue-800 p-2 rounded-full hover:bg-blue-600 transition-colors"
                    aria-label="Facebook profile">
                    <Facebook className="w-5 h-5" />
                  </a>
                )}
                {athlete.socialsLinks?.twitter && (
                  <a href={athlete.socialsLinks.twitter} target="_blank" rel="noopener noreferrer" 
                    className="bg-blue-800 p-2 rounded-full hover:bg-blue-600 transition-colors"
                    aria-label="Twitter profile">
                    <Twitter className="w-5 h-5" />
                  </a>
                )}
                {athlete.socialsLinks?.instagram && (
                  <a href={athlete.socialsLinks.instagram} target="_blank" rel="noopener noreferrer" 
                    className="bg-blue-800 p-2 rounded-full hover:bg-blue-600 transition-colors"
                    aria-label="Instagram profile">
                    <Instagram className="w-5 h-5" />
                  </a>
                )}
                {athlete.socialsLinks?.website && (
                  <a href={athlete.socialsLinks.website} target="_blank" rel="noopener noreferrer" 
                    className="bg-blue-800 p-2 rounded-full hover:bg-blue-600 transition-colors"
                    aria-label="Personal website">
                    <LinkIcon className="w-5 h-5" />
                  </a>
                )}
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Main content */}
      <div className="container mx-auto px-4 py-8">
        <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
          <TabsList className="w-full max-w-3xl mx-auto bg-white mb-6">
            <TabsTrigger value="info" className="flex-1">
              <Info className="w-4 h-4 mr-2" />
              Bio & Info
            </TabsTrigger>
            <TabsTrigger value="results" className="flex-1">
              <Trophy className="w-4 h-4 mr-2" />
              Results
            </TabsTrigger>
            <TabsTrigger value="progression" className="flex-1">
              <TrendingUp className="w-4 h-4 mr-2" />
              Progression
            </TabsTrigger>
          </TabsList>
          
          {/* Bio & Info Tab */}
          <TabsContent value="info" className="mt-6">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <div className="md:col-span-1">
                <Card>
                  <CardHeader className="bg-gray-50 border-b">
                    <CardTitle className="text-lg">Personal Information</CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-4 pt-4">
                    <div className="flex justify-between items-center">
                      <span className="text-gray-500">Date of Birth:</span>
                      <span className="font-medium">
                        {athlete.dateOfBirth 
                          ? `${format(new Date(athlete.dateOfBirth), 'dd MMM yyyy')} (${calculateAge(athlete.dateOfBirth)} years)`
                          : 'N/A'}
                      </span>
                    </div>
                    <div className="flex justify-between items-center">
                      <span className="text-gray-500">Place of Birth:</span>
                      <span className="font-medium">{athlete.placeOfBirth || 'N/A'}</span>
                    </div>
                    <div className="flex justify-between items-center">
                      <span className="text-gray-500">Height:</span>
                      <span className="font-medium">{athlete.height ? `${athlete.height} cm` : 'N/A'}</span>
                    </div>
                    <div className="flex justify-between items-center">
                      <span className="text-gray-500">Weight:</span>
                      <span className="font-medium">{athlete.weight ? `${athlete.weight} kg` : 'N/A'}</span>
                    </div>
                    <div className="flex justify-between items-center">
                      <span className="text-gray-500">Coach:</span>
                      <span className="font-medium">{athlete.coach || 'N/A'}</span>
                    </div>
                    <div className="flex justify-between items-center">
                      <span className="text-gray-500">Club:</span>
                      <span className="font-medium">{athlete.club || 'N/A'}</span>
                    </div>
                  </CardContent>
                </Card>

                <Card className="mt-6">
                  <CardHeader className="bg-gray-50 border-b">
                    <CardTitle className="text-lg">Championships</CardTitle>
                  </CardHeader>
                  <CardContent className="pt-4">
                    {athlete.championships && athlete.championships.length > 0 ? (
                      <ul className="space-y-3">
                        {athlete.championships.map((championship) => (
                          <li key={championship.id} className="flex items-center">
                            {renderMedalColor(championship.medal)}
                            <div>
                              <p className="font-medium">{championship.name} {championship.year}</p>
                              <p className="text-sm text-gray-500">{championship.place} - {championship.location}</p>
                            </div>
                          </li>
                        ))}
                      </ul>
                    ) : (
                      <p className="text-gray-500">No championship appearances</p>
                    )}
                  </CardContent>
                </Card>

                <Card className="mt-6">
                  <CardHeader className="bg-gray-50 border-b">
                    <CardTitle className="text-lg">Career Highlights</CardTitle>
                  </CardHeader>
                  <CardContent className="pt-4">
                    {athlete.careerHighlights && athlete.careerHighlights.length > 0 ? (
                      <ul className="space-y-2">
                        {athlete.careerHighlights.map((highlight, index) => (
                          <li key={index} className="flex">
                            <Award className="w-4 h-4 text-yellow-500 mr-2 mt-1 flex-shrink-0" />
                            <span>{highlight}</span>
                          </li>
                        ))}
                      </ul>
                    ) : (
                      <p className="text-gray-500">No career highlights available</p>
                    )}
                  </CardContent>
                </Card>
              </div>

              <div className="md:col-span-2">
                <Card>
                  <CardHeader className="bg-gray-50 border-b">
                    <CardTitle className="text-lg">Biography</CardTitle>
                  </CardHeader>
                  <CardContent className="pt-4">
                    {athlete.biography ? (
                      <div className="prose prose-blue max-w-none">
                        <p>{athlete.biography}</p>
                      </div>
                    ) : (
                      <p className="text-gray-500">No biography available</p>
                    )}
                  </CardContent>
                </Card>

                <Card className="mt-6">
                  <CardHeader className="bg-gray-50 border-b">
                    <CardTitle className="text-lg">Personal Bests</CardTitle>
                  </CardHeader>
                  <CardContent className="pt-4">
                    {athlete.personalBests && athlete.personalBests.length > 0 ? (
                      <div className="overflow-x-auto">
                        <table className="w-full text-sm">
                          <thead>
                            <tr className="border-b">
                              <th className="text-left py-2 font-semibold text-gray-600">Event</th>
                              <th className="text-left py-2 font-semibold text-gray-600">Mark</th>
                              <th className="text-left py-2 font-semibold text-gray-600">Venue</th>
                              <th className="text-left py-2 font-semibold text-gray-600">Date</th>
                              <th className="text-left py-2 font-semibold text-gray-600">Notes</th>
                            </tr>
                          </thead>
                          <tbody>
                            {athlete.personalBests.map((pb, index) => (
                              <tr key={index} className="border-b last:border-0 hover:bg-gray-50">
                                <td className="py-3">{pb.event}</td>
                                <td className="py-3 font-medium">{pb.mark}</td>
                                <td className="py-3">{pb.venue}</td>
                                <td className="py-3">{pb.date}</td>
                                <td className="py-3 text-blue-600">{pb.notes}</td>
                              </tr>
                            ))}
                          </tbody>
                        </table>
                      </div>
                    ) : (
                      <p className="text-gray-500">No personal bests available</p>
                    )}
                  </CardContent>
                </Card>
              </div>
            </div>
          </TabsContent>
          
          {/* Results Tab */}
          <TabsContent value="results" className="mt-6">
            <div className="flex justify-between items-center mb-4">
              <h2 className="text-xl font-bold">Competition Results</h2>
              <select 
                className="border rounded-md p-2"
                value={selectedYear}
                onChange={(e) => handleYearChange(parseInt(e.target.value))}
              >
                {Array.from({ length: 5 }, (_, i) => new Date().getFullYear() - i).map((year) => (
                  <option key={year} value={year}>{year}</option>
                ))}
              </select>
            </div>
            
            <Card>
              <CardHeader className="bg-gray-50 border-b">
                <CardTitle className="text-lg">Recent Competitions</CardTitle>
                <CardDescription>Latest performances in {selectedYear}</CardDescription>
              </CardHeader>
              <CardContent className="pt-0">
                {athlete.recentCompetitions && athlete.recentCompetitions.length > 0 ? (
                  <div className="overflow-x-auto">
                    <table className="w-full text-sm">
                      <thead>
                        <tr className="border-b bg-gray-50">
                          <th className="text-left py-3 px-2 font-semibold text-gray-600">Date</th>
                          <th className="text-left py-3 px-2 font-semibold text-gray-600">Competition</th>
                          <th className="text-left py-3 px-2 font-semibold text-gray-600">Event</th>
                          <th className="text-left py-3 px-2 font-semibold text-gray-600">Place</th>
                          <th className="text-left py-3 px-2 font-semibold text-gray-600">Mark</th>
                          <th className="text-left py-3 px-2 font-semibold text-gray-600">Venue</th>
                          <th className="text-left py-3 px-2 font-semibold text-gray-600">Points</th>
                        </tr>
                      </thead>
                      <tbody>
                        {athlete.recentCompetitions.map((result) => (
                          <tr key={result.id} className="border-b last:border-0 hover:bg-gray-50">
                            <td className="py-3 px-2">{result.date}</td>
                            <td className="py-3 px-2">{result.competition}</td>
                            <td className="py-3 px-2">{result.event}</td>
                            <td className="py-3 px-2 font-medium">
                              {result.place === '1st' ? (
                                <span className="text-yellow-600">{result.place}</span>
                              ) : result.place === '2nd' ? (
                                <span className="text-gray-500">{result.place}</span>
                              ) : result.place === '3rd' ? (
                                <span className="text-amber-700">{result.place}</span>
                              ) : (
                                result.place
                              )}
                            </td>
                            <td className="py-3 px-2 font-medium">
                              {result.mark}
                              {result.wind && <span className="ml-1 text-gray-500">({result.wind})</span>}
                            </td>
                            <td className="py-3 px-2">{result.venue}</td>
                            <td className="py-3 px-2">{result.points || '-'}</td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                ) : (
                  <p className="text-gray-500 p-4">No competition results available for {selectedYear}</p>
                )}
              </CardContent>
            </Card>

            <div className="mt-6 flex justify-end">
              <Button variant="outline">
                <Calendar className="w-4 h-4 mr-2" />
                View Full Competition History
              </Button>
            </div>
          </TabsContent>
          
          {/* Progression Tab */}
          <TabsContent value="progression" className="mt-6">
            <Card>
              <CardHeader className="bg-gray-50 border-b flex flex-col sm:flex-row justify-between items-start sm:items-center">
                <div>
                  <CardTitle className="text-lg">Performance Progression</CardTitle>
                  <CardDescription>Season best marks by year for {selectedEvent}</CardDescription>
                </div>
                <div className="mt-2 sm:mt-0">
                  <select 
                    className="border rounded-md p-2 text-sm"
                    value={selectedEvent}
                    onChange={(e) => handleEventChange(e.target.value)}
                  >
                    <option value={athlete.mainEvent}>{athlete.mainEvent}</option>
                    {athlete.otherEvents.map((event, i) => (
                      <option key={i} value={event}>{event}</option>
                    ))}
                  </select>
                </div>
              </CardHeader>
              <CardContent className="pt-6">
                {athlete.seasonBests && athlete.seasonBests.length > 0 ? (
                  <div>
                    {/* Simplified chart - in a real app, use a chart library like recharts */}
                    <div className="h-72 bg-gray-100 mb-8 rounded-md p-6 flex items-end justify-between">
                      {athlete.seasonBests.map((sb, index) => {
                        // For demonstration purposes - in a real app you'd calculate this properly
                        // Here we're simulating a downward progression (better times) for 400m hurdles
                        const baseHeight = 40; // Minimum height percentage
                        const maxHeight = 90;
                        const height = maxHeight - (index * ((maxHeight - baseHeight) / athlete.seasonBests.length));
                        
                        return (
                          <div key={index} className="flex flex-col items-center">
                            <div 
                              className="bg-blue-600 w-16 rounded-t-md relative group"
                              style={{ height: `${height}%` }}
                            >
                              <div className="absolute -top-10 left-1/2 transform -translate-x-1/2 bg-blue-900 text-white px-2 py-1 rounded text-xs opacity-0 group-hover:opacity-100 transition-opacity whitespace-nowrap">
                                {sb.mark}
                              </div>
                            </div>
                            <span className="text-xs mt-2 font-medium">{sb.year}</span>
                            <span className="text-xs mt-1">{sb.mark}</span>
                          </div>
                        );
                      })}
                    </div>

                    <div className="overflow-x-auto">
                      <table className="w-full text-sm">
                        <thead>
                          <tr className="border-b bg-gray-50">
                            <th className="text-left py-3 px-4 font-semibold text-gray-600">Year</th>
                            <th className="text-left py-3 px-4 font-semibold text-gray-600">Mark</th>
                            <th className="text-left py-3 px-4 font-semibold text-gray-600">Competition</th>
                            <th className="text-left py-3 px-4 font-semibold text-gray-600">Venue</th>
                            <th className="text-left py-3 px-4 font-semibold text-gray-600">Date</th>
                          </tr>
                        </thead>
                        <tbody>
                          {athlete.seasonBests.map((sb, index) => (
                            <tr key={index} className="border-b last:border-0 hover:bg-gray-50">
                              <td className="py-3 px-4 font-medium">{sb.year}</td>
                              <td className="py-3 px-4 font-medium">{sb.mark}</td>
                              <td className="py-3 px-4">{sb.competition}</td>
                              <td className="py-3 px-4">{sb.venue || '-'}</td>
                              <td className="py-3 px-4">{sb.date || '-'}</td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                  </div>
                ) : (
                  <p className="text-gray-500">No progression data available</p>
                )}
              </CardContent>
            </Card>
            
            {/* Historical Progression with Bar Chart */}
            <Card className="mt-6">
              <CardHeader className="bg-gray-50 border-b">
                <CardTitle className="text-lg">Event Improvement Rate</CardTitle>
                <CardDescription>Career trajectory in {athlete.mainEvent}</CardDescription>
              </CardHeader>
              <CardContent className="pt-6">
                <div className="h-8 w-full bg-gray-200 rounded-full overflow-hidden">
                  <div 
                    className="h-full bg-gradient-to-r from-blue-500 to-blue-700 flex items-center justify-end px-3"
                    style={{ width: "88%" }}
                  >
                    <span className="text-xs text-white font-medium">88%</span>
                  </div>
                </div>
                <p className="text-sm text-gray-500 mt-2">
                  Career improvement rate based on first recorded performance to personal best
                </p>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
} 