import { Component, OnInit } from '@angular/core';
import { Game } from './shared_interfaces';

@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.css']
})
export class AppComponent implements OnInit {
  title: string = 'Stacks by Stacks';
  games: Array<Game>;

  async ngOnInit() {
    var url = new URL('https://stacksbystacks.com/Sql.php');
    url.searchParams.append('columns', 'game_date,home_team_id,home_score,away_score,home_team_name,away_team_name,play_status');
    url.searchParams.append('table', 'games_with_team_names');
    url.searchParams.append('order', 'game_date desc');
  	let response = await fetch(url.href);
  	this.games = await response.json();
  }
}
