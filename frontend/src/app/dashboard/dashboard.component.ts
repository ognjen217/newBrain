import { Component, HostListener, OnInit } from '@angular/core';
import { DashboardService } from '../services/dashboard.service';

@Component({
  selector: 'app-dashboard',
  templateUrl: './dashboard.component.html',
  styleUrls: ['./dashboard.component.css']
})
export class DashboardComponent implements OnInit {
  status: any;
  controlMessage: string = 'No command received...';

  constructor(private dashboardService: DashboardService) {}

  ngOnInit() {
    this.getStatus();
    // Poll status every second (adjust as needed)
    setInterval(() => {
      this.getStatus();
    }, 1000);
  }

  getStatus() {
    this.dashboardService.getStatus().subscribe(data => {
      this.status = data;
    }, err => {
      console.error('Error fetching status', err);
    });
  }

  @HostListener('window:keydown', ['$event'])
  handleKeyDown(event: KeyboardEvent) {
    const key = event.key.toUpperCase();
    if (['W', 'A', 'S', 'D'].includes(key)) {
      this.controlMessage = 'Received command: ' + key;
      this.dashboardService.sendControl(key).subscribe(data => {
        console.log('Control response:', data);
      }, err => {
        console.error('Control error:', err);
      });
    }
  }
}
