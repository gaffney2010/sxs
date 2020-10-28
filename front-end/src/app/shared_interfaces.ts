export interface GameDate {
  game_date: bigint;
}

export interface Game {
  home_score: bigint;
  away_score: bigint;
  home_team_name: string;
  away_team_name: string;
  play_status: string;  // Enum
}
