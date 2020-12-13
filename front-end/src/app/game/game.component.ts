import { Component, OnInit, Input } from '@angular/core';
import { Game, Stack } from '../shared_interfaces';

@Component({
  selector: 'app-game',
  templateUrl: './game.component.html',
  styleUrls: ['./game.component.css']
})
export class GameComponent implements OnInit {
  @Input() game_data: Game;
  stacks: Array<Stack>;

  constructor() { }

  get scoresExist() {
    return this.game_data.play_status != "UPCOMING";
  }

  get isAwayWon() {
    if (this.game_data.play_status != "PAST") return false;
    return this.game_data.home_score > this.game_data.away_score;
  }

  get isHomeWon() {
    if (this.game_data.play_status != "PAST") return false;
    return this.game_data.home_score < this.game_data.away_score;
  }

  spread(stack: Stack) {
    let result = "";
    if (stack.spread_favorite == stack.predicted_winner_id_with_spread) {
      result += "-";
    } else {
      result += "+";
    }
    result += stack.spread_amt;
    return result;
  }

  async ngOnInit() {
    var url = new URL('https://stacksbystacks.com/Sql.php');
    url.searchParams.append('columns', 'expert_name,expert_id,affiliate,link,predicted_winner_name,predicted_winner_id_with_spread,spread_favorite,spread_amt');
    url.searchParams.append('table', 'stacks_with_stacks');
    url.searchParams.append('where', 'game_date=' + this.game_data.game_date + ' and home_team_id=' + this.game_data.home_team_id);
  	let response = await fetch(url.href);
  	this.stacks = await response.json();
  }

}
