import { BrowserModule } from '@angular/platform-browser';
import { NgModule } from '@angular/core';

import { AppComponent } from './app.component';
import { GameComponent } from './game/game.component';
import { StacksComponent } from './stacks/stacks.component';
import { RouterModule } from '@angular/router';
import { AboutComponent } from './about/about.component';
import { ExpertComponent } from './expert/expert.component';
import { ExpertIdComponent } from './expert-id/expert-id.component';

@NgModule({
  declarations: [
    AppComponent,
    GameComponent,
    StacksComponent,
    AboutComponent,
    ExpertComponent,
    ExpertIdComponent
  ],
  imports: [
    BrowserModule,
    RouterModule.forRoot([
      {path: 'stacks', component: StacksComponent},
      {path: 'about', component: AboutComponent},
      {path: 'experts', component: ExpertComponent},
      {path: 'expert/:expert_id', component: ExpertIdComponent},
      {path: '', redirectTo: '/stacks', pathMatch: 'full'},
    ]),
  ],
  providers: [],
  bootstrap: [AppComponent]
})
export class AppModule { }
