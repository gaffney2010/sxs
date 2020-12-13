import { Component, OnInit, Input } from '@angular/core';
import { Expert } from '../shared_interfaces';

@Component({
  selector: 'app-expert',
  templateUrl: './expert.component.html',
  styleUrls: ['./expert.component.css']
})
export class ExpertComponent implements OnInit {
  experts: Array<Expert>;

  constructor() { }

  async ngOnInit() {
    var url = new URL('https://stacksbystacks.com/Sql.php');
    url.searchParams.append('columns', 'expert_id,expert_text,score');
    url.searchParams.append('table', 'expert_with_records');
    url.searchParams.append('order', 'score desc');
  	let response = await fetch(url.href);
  	this.experts = await response.json();
  }

}
