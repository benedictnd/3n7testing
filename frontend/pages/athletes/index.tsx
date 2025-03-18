import React, { useState } from 'react';
import Link from 'next/link';
import Image from 'next/image';
import Head from 'next/head';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { Card, CardContent } from '@/components/ui/card';
import { Search, Filter, Flag } from 'lucide-react';
import { mockAthletes, AthleteData } from '../../lib/mock-athlete-data';

export default function AthletesList() {
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedCountry, setSelectedCountry] = useState<string | null>(null);
  const [selectedEvent, setSelectedEvent] = useState<string | null>(null);

  // Extract unique countries and events for filters
  const countries = Array.from(new Set(Object.values(mockAthletes).map((athlete: AthleteData) => athlete.country)));
  const events = Array.from(new Set(
    Object.values(mockAthletes).flatMap((athlete: AthleteData) => 
      [athlete.mainEvent, ...athlete.otherEvents]
    )
  ));

  // Filter athletes based on search and filters
  const filteredAthletes = Object.values(mockAthletes).filter((athlete: AthleteData) => {
    // Search filter
    if (searchQuery && !athlete.name.toLowerCase().includes(searchQuery.toLowerCase())) {
      return false;
    }
    
    // Country filter
    if (selectedCountry && athlete.country !== selectedCountry) {
      return false;
    }
    
    // Event filter
    if (selectedEvent && !([athlete.mainEvent, ...athlete.otherEvents].includes(selectedEvent))) {
      return false;
    }
    
    return true;
  });

  const clearFilters = () => {
    setSearchQuery('');
    setSelectedCountry(null);
    setSelectedEvent(null);
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <Head>
        <title>Athletes | 3&7 Training Platform</title>
      </Head>

      <div className="container mx-auto px-4 py-8">
        <h1 className="text-3xl font-bold mb-2">Athletes</h1>
        <p className="text-gray-600 mb-6">Browse and discover top athletes in our platform</p>

        {/* Search and Filters */}
        <div className="bg-white p-4 rounded-lg shadow-sm mb-8">
          <div className="flex flex-col md:flex-row gap-4 mb-4">
            <div className="relative flex-grow">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" size={18} />
              <Input
                placeholder="Search athletes by name..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="pl-10"
              />
            </div>
            <div className="flex gap-4 flex-wrap">
              <select
                className="border rounded-md p-2 text-sm bg-white"
                value={selectedCountry || ''}
                onChange={(e) => setSelectedCountry(e.target.value || null)}
              >
                <option value="">All Countries</option>
                {countries.map((country) => (
                  <option key={country} value={country}>
                    {country}
                  </option>
                ))}
              </select>
              <select
                className="border rounded-md p-2 text-sm bg-white"
                value={selectedEvent || ''}
                onChange={(e) => setSelectedEvent(e.target.value || null)}
              >
                <option value="">All Events</option>
                {events.map((event) => (
                  <option key={event} value={event}>
                    {event}
                  </option>
                ))}
              </select>
              <Button variant="outline" onClick={clearFilters} size="sm">
                Clear Filters
              </Button>
            </div>
          </div>
          <div className="text-sm text-gray-500">
            Showing {filteredAthletes.length} athlete{filteredAthletes.length !== 1 ? 's' : ''}
            {selectedCountry && ` from ${selectedCountry}`}
            {selectedEvent && ` in ${selectedEvent}`}
          </div>
        </div>

        {/* Athletes Grid */}
        <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-6">
          {filteredAthletes.map((athlete: AthleteData) => (
            <Link 
              href={`/athlete/${athlete.id}`} 
              key={athlete.id}
              className="transition-transform hover:scale-105"
            >
              <Card className="overflow-hidden h-full hover:shadow-md transition-shadow">
                <div className="relative h-48 bg-blue-100">
                  <Image
                    src={athlete.profileImage}
                    alt={athlete.name}
                    fill
                    style={{ objectFit: 'cover' }}
                  />
                  <div className="absolute top-0 right-0 bg-blue-900 text-white text-xs px-2 py-1 m-2 rounded">
                    #{athlete.worldRanking}
                  </div>
                  <div className="absolute bottom-0 left-0 right-0 bg-gradient-to-t from-blue-900 to-transparent p-2">
                    <div className="flex items-center">
                      <Flag className="w-3 h-3 text-white mr-1" />
                      <span className="text-xs text-white">{athlete.country}</span>
                    </div>
                  </div>
                </div>
                <CardContent className="p-4">
                  <h3 className="font-bold truncate">{athlete.name}</h3>
                  <p className="text-sm text-gray-600">{athlete.mainEvent}</p>
                  <div className="flex justify-between items-center mt-2 text-xs text-gray-500">
                    <span>PB: {athlete.personalBests[0]?.mark || 'N/A'}</span>
                    <span>SB: {athlete.seasonBests[0]?.mark || 'N/A'}</span>
                  </div>
                </CardContent>
              </Card>
            </Link>
          ))}
        </div>

        {filteredAthletes.length === 0 && (
          <div className="text-center py-12 bg-white rounded-lg shadow-sm">
            <p className="text-lg text-gray-600">No athletes found matching your criteria</p>
            <Button variant="outline" onClick={clearFilters} className="mt-4">
              Clear Filters
            </Button>
          </div>
        )}
      </div>
    </div>
  );
} 