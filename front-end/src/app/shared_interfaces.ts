
export interface Game {
  game_key: string;
  game_date: bigint;
  home_score: bigint;
  away_score: bigint;
  home_team_name: string;
  away_team_name: string;
  play_status: string;  // Enum
}

export interface Expert {
  expert_id: bigint;
  expert_text: string;
  score: bigint;
}

export interface ExpertDetails {
  expert_id: bigint;
  game_date: bigint;
  home_team_name: string;
  away_team_name: string;
  home_score: bigint;
  away_score: bigint;
  spread_favorite: bigint;
  spread_amt: bigint;
  link: string;
  predicted_winner_id_with_spread: bigint;
  predicted_winner_name: string;
}

export interface Stack {
  expert_name: string;
  expert_id: bigint;
  affiliate: string;
  link: string;
  predicted_winner_name: string;
  predicted_winner_id_with_spread: bigint;
  spread_favorite: bigint;
  spread_amt: number;
  consensus: string;
}
