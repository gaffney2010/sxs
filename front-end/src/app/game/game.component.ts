import { Component, OnInit, Input } from '@angular/core';
import { Game } from '../shared_interfaces';

@Component({
  selector: 'app-game',
  templateUrl: './game.component.html',
  styleUrls: ['./game.component.css']
})
export class GameComponent implements OnInit {
  @Input() game_data: Game;

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

  ngOnInit(): void {
  }

}
