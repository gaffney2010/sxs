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
  consensus: string;

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

  formattedName(stack: Stack) {
    var words = stack.expert_name.split(" ")
    var result = ""
    for (var i = 0; i < words.length; i++) {
      if (result != "") result += " "
      result += words[i][0].toUpperCase() + words[i].substr(1);
    }
    return result;
  }

  async ngOnInit() {
    var url = new URL('https://stacksbystacks.com/Sql.php');
    url.searchParams.append('columns', 'expert_name,expert_id,affiliate,link,predicted_winner_name,predicted_winner_id,money_line,consensus');
    url.searchParams.append('table', 'swsws_table');
    // Must do key/value over where because string.
    url.searchParams.append('key', "game_key");
    url.searchParams.append('value', this.game_data.game_key);
    url.searchParams.append('order', 'score desc');
  	let response = await fetch(url.href);
  	this.stacks = await response.json();
  	this.consensus = this.stacks[0].consensus;
  }

}
