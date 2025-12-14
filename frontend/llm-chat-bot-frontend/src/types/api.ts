export interface CarRecommendation {
  name: string;
  price_per_day: number;
  seats: number;
  reasoning: string;
}

export interface Query {
  prompt: string;
}

export interface ApiResponse {
  status: string;
  query: Query;
  results: CarRecommendation[];
}
