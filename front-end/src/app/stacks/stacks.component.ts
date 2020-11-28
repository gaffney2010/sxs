import { Component, OnInit } from '@angular/core';
import { Game } from './shared_interfaces';

@Component({
  selector: 'app-stacks',
  templateUrl: './stacks.component.html',
  styleUrls: ['./stacks.component.css']
})
export class StacksComponent implements OnInit {
  games: Array<Game>;

  constructor() { }

  ngOnInit(): void {
    var url = new URL('https://stacksbystacks.com/Sql.php');
    url.searchParams.append('columns', 'game_date,home_team_id,home_score,away_score,home_team_name,away_team_name,play_status');
    url.searchParams.append('table', 'games_with_team_names');
    url.searchParams.append('order', 'game_date desc');
  	let response = await fetch(url.href);
  	this.games = await response.json();
  }
}
