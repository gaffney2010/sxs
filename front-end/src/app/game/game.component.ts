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

  async ngOnInit() {
    var url = new URL('https://stacksbystacks.com/Sql.php');
    url.searchParams.append('columns', 'expert_name,expert_id,affiliate,link,predicted_winner_name,predicted_winner_id,money_line');
    url.searchParams.append('table', 'stacks_with_stacks_with_stacks');
    // Must do key/value over where because string.
    url.searchParams.append('key', "game_key");
    url.searchParams.append('value', this.game_data.game_key);
    url.searchParams.append('order', 'score desc');
  	let response = await fetch(url.href);
  	this.stacks = await response.json();
  }

}
