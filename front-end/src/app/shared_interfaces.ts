
export interface Game {
  game_date: bigint;
  home_team_id: bigint;
  home_score: bigint;
  away_score: bigint;
  home_team_name: string;
  away_team_name: string;
  play_status: string;  // Enum
}

export interface Stack {
  expert_name: string;
  affiliate: string;
  link: string;
  predicted_winner_name: string;
  predicted_winner_id_with_spread: bigint;
  spread_favorite: bigint;
  spread_amt: number;
}
