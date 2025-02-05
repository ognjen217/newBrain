import { Component, HostListener, OnInit } from '@angular/core';
import { DashboardService } from '../services/dashboard.service';

@Component({
  selector: 'app-dashboard',
  templateUrl: './dashboard.component.html',
  styleUrls: ['./dashboard.component.css']
})
export class DashboardComponent implements OnInit {
  status: any = {};
  controlMessage: string = 'No command received...';
  
  // Gauge angles (in degrees)
  steeringAngle: number = 0;
  motorAngle: number = 0;

  // Define maximum expected values for mapping gauge angles
  maxSteering: number = 45; // Assume steering ranges from -45 to +45 degrees
  maxMotorSpeed: number = 10; // Assume motor speed ranges from 0 to 10 km/h

  constructor(private dashboardService: DashboardService) { }

  ngOnInit(): void {
    this.fetchStatus();
    setInterval(() => this.fetchStatus(), 500);
  }

  fetchStatus(): void {
    this.dashboardService.getStatus().subscribe(data => {
      this.status = data;
      this.updateGauges();
    }, err => {
      console.error('Error fetching status', err);
    });
  }

  updateGauges(): void {
    // Update steering gauge:
    const steering = this.status?.sensor_data?.steering || 0;
    // Clamp steering to -maxSteering...maxSteering
    const clampedSteering = Math.max(-this.maxSteering, Math.min(this.maxSteering, steering));
    // For simplicity, assume that -maxSteering maps to -45deg and +maxSteering maps to 45deg
    this.steeringAngle = clampedSteering; // Direct mapping

    // Update motor speed gauge:
    const speed = this.status?.motor_status?.current_speed || 0;
    // Map speed 0 -> -45deg, maxMotorSpeed -> 45deg
    let angle = ((speed / this.maxMotorSpeed) * 90) - 45;
    angle = Math.max(-45, Math.min(45, angle));
    this.motorAngle = angle;
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
