import { Component, OnInit, Input } from '@angular/core';
import { GameDate, Game } from '../shared_interfaces';

@Component({
  selector: 'app-game-date',
  templateUrl: './game-date.component.html',
  styleUrls: ['./game-date.component.css']
})
export class GameDateComponent implements OnInit {
  @Input() game_date: GameDate;
  games: Array<Game>;

  constructor() { }

  async ngOnInit() {
    var url = new URL('https://stacksbystacks.com/Sql.php');
    url.searchParams.append('columns', 'home_score,away_score,home_team_name,away_team_name,play_status');
    url.searchParams.append('table', 'games_with_team_names');
    url.searchParams.append('where', 'game_date=' + this.game_date);
  	let response = await fetch(url.href);
  	this.games = await response.json();
  }

}
