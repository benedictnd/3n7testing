// Mock athlete data that resembles World Athletics profiles

export interface PersonalBest {
  event: string;
  mark: string;
  venue: string;
  date: string;
  notes?: string;
}

export interface CompetitionResult {
  id: string;
  date: string;
  competition: string;
  event: string;
  venue: string;
  place: string;
  mark: string;
  wind?: string;
  points?: number;
  notes?: string;
}

export interface SeasonBest {
  year: number;
  mark: string;
  competition: string;
  venue?: string;
  date?: string;
}

export interface Championship {
  id: string;
  name: string;
  year: number;
  location: string;
  place: string;
  medal?: 'gold' | 'silver' | 'bronze';
}

export interface AthleteData {
  id: string;
  name: string;
  country: string;
  countryCode: string;
  dateOfBirth: string;
  placeOfBirth: string;
  discipline: string;
  mainEvent: string;
  otherEvents: string[];
  height: number;
  weight: number;
  coach: string;
  club: string;
  biography: string;
  worldRanking: number;
  personalBests: PersonalBest[];
  seasonBests: SeasonBest[];
  championships: Championship[];
  careerHighlights: string[];
  recentCompetitions: CompetitionResult[];
  socialsLinks: {
    facebook?: string;
    twitter?: string;
    instagram?: string;
    website?: string;
  };
  profileImage: string;
}

export const karstenWarholm: AthleteData = {
  id: "14479487",
  name: "Karsten WARHOLM",
  country: "Norway",
  countryCode: "NOR",
  dateOfBirth: "1996-02-28",
  placeOfBirth: "Ulsteinvik, Norway",
  discipline: "Sprints, Hurdles",
  mainEvent: "400m Hurdles",
  otherEvents: ["400m", "300m Hurdles"],
  height: 187,
  weight: 80,
  coach: "Leif Olav Alnes",
  club: "Dimna IL",
  biography: "Karsten Warholm is a Norwegian athlete who specializes in the 400 metres hurdles. He is the world record holder with a time of 45.94 seconds, set at the 2020 Summer Olympics in Tokyo on 3 August 2021. He is the first person in history to run the 400 metres hurdles in under 46 seconds. Warholm is the 2020 Olympic champion, two-time World champion (2017 and 2019), and two-time European champion (2018 and 2022) in the event. Warholm won gold at the 2018 World Indoor Championships and silver at the 2022 World Indoor Championships in the 400 metres. He has broken the world record in the 400 metres hurdles three times.",
  worldRanking: 1,
  personalBests: [
    { event: "400m Hurdles", mark: "45.94", venue: "Tokyo (JPN)", date: "03 AUG 2021", notes: "WR" },
    { event: "400m", mark: "44.52", venue: "Zurich (SUI)", date: "29 AUG 2019" },
    { event: "300m Hurdles", mark: "33.26", venue: "Oslo (NOR)", date: "13 JUN 2019" }
  ],
  seasonBests: [
    { year: 2023, mark: "46.51", competition: "World Championships", venue: "Budapest (HUN)", date: "21 AUG 2023" },
    { year: 2022, mark: "46.29", competition: "Stockholm Diamond League", venue: "Stockholm (SWE)", date: "30 JUN 2022" },
    { year: 2021, mark: "45.94", competition: "Olympic Games", venue: "Tokyo (JPN)", date: "03 AUG 2021" },
    { year: 2020, mark: "46.87", competition: "Stockholm Diamond League", venue: "Stockholm (SWE)", date: "23 AUG 2020" },
    { year: 2019, mark: "46.92", competition: "Zurich Diamond League", venue: "Zurich (SUI)", date: "29 AUG 2019" }
  ],
  championships: [
    { id: "1", name: "Olympic Games", year: 2021, location: "Tokyo (JPN)", place: "1st", medal: "gold" },
    { id: "2", name: "World Championships", year: 2022, location: "Eugene (USA)", place: "7th" },
    { id: "3", name: "World Championships", year: 2019, location: "Doha (QAT)", place: "1st", medal: "gold" },
    { id: "4", name: "World Championships", year: 2017, location: "London (GBR)", place: "1st", medal: "gold" },
    { id: "5", name: "European Championships", year: 2018, location: "Berlin (GER)", place: "1st", medal: "gold" }
  ],
  careerHighlights: [
    "Olympic Champion - Tokyo 2020 (400m Hurdles)",
    "World Record Holder - 45.94 (400m Hurdles)",
    "World Champion - Doha 2019 & London 2017 (400m Hurdles)",
    "European Champion - Berlin 2018 (400m Hurdles)",
    "Diamond League Champion - 2019, 2021"
  ],
  recentCompetitions: [
    { 
      id: "comp1", 
      date: "03 JUL 2023", 
      competition: "Gyulai István Memorial",
      event: "400m Hurdles", 
      venue: "Székesfehérvár (HUN)", 
      place: "1st", 
      mark: "47.78",
      points: 1218
    },
    { 
      id: "comp2", 
      date: "15 JUN 2023", 
      competition: "Oslo Bislett Games",
      event: "400m Hurdles", 
      venue: "Oslo (NOR)", 
      place: "1st", 
      mark: "46.52",
      points: 1302
    },
    { 
      id: "comp3", 
      date: "02 JUN 2023", 
      competition: "Golden Gala",
      event: "400m Hurdles", 
      venue: "Florence (ITA)", 
      place: "1st", 
      mark: "47.31",
      points: 1258
    },
    { 
      id: "comp4", 
      date: "05 MAY 2023", 
      competition: "Doha Diamond League",
      event: "400m Hurdles", 
      venue: "Doha (QAT)", 
      place: "1st", 
      mark: "47.82",
      points: 1215
    }
  ],
  socialsLinks: {
    facebook: "https://www.facebook.com/kwarholm",
    instagram: "https://www.instagram.com/kwarholm",
    twitter: "https://twitter.com/kwarholm"
  },
  profileImage: "/images/karsten-warholm.jpg"
};

export const mockAthletes: Record<string, AthleteData> = {
  "14479487": karstenWarholm,
  // Add more athletes as needed
}; 