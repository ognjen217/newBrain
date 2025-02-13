// Copyright (c) 2019, Bosch Engineering Center Cluj and BFMC orginazers
// All rights reserved.

// Redistribution and use in source and binary forms, with or without
// modification, are permitted provided that the following conditions are met:

//  1. Redistributions of source code must retain the above copyright notice, this
//    list of conditions and the following disclaimer.

//  2. Redistributions in binary form must reproduce the above copyright notice,
//     this list of conditions and the following disclaimer in the documentation
//     and/or other materials provided with the distribution.

// 3. Neither the name of the copyright holder nor the names of its
//    contributors may be used to endorse or promote products derived from
//     this software without specific prior written permission.

// THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
// AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
// IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
// DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
// FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
// DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
// SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
// CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
// OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
// OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

import { Component, ViewChild, HostListener } from '@angular/core';
import { WebSocketService } from './webSocket/web-socket.service';
import { ClusterComponent } from './cluster/cluster.component';
import { TableComponent } from './table/table.component';
import * as CryptoJS from 'crypto-js';
import { Subscription } from 'rxjs';
import { FormsModule } from '@angular/forms';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.css'],
  standalone: true,
  imports: [FormsModule, CommonModule]
})

export class AppComponent {
  title = 'dashboard';
  isAuthenticated = false;
  yoloImage: string = '';
  houghImage: string = '';
  enteredPassword = '';
  correctPassword = 'U2FsdGVkX18Lrd7U4IqjmFUNVH7aGbw7SPsLXHb2qlU=';
  private secretKey = 'ThisIsTheKey';
  private sessionAccessSubscription: Subscription | undefined;

  @ViewChild(ClusterComponent) clusterComponent!: ClusterComponent;
  @ViewChild(TableComponent) tableComponent!: TableComponent;

  constructor(private webSocketService: WebSocketService) {
    this.listenForCameraFeed();
    this.listenForSessionAccess();
  }

  listenForCameraFeed() {
    this.webSocketService.getMessages().subscribe((message: any) => {
      try {
        const data = JSON.parse(message.data);
        if (data.parity === 'even') {
          this.yoloImage = `data:image/jpeg;base64,${data.image}`;
        } else if (data.parity === 'odd') {
          this.houghImage = `data:image/jpeg;base64,${data.image}`;
        }
      } catch (error) {
        console.error('Error parsing incoming WebSocket data:', error);
      }
    });
  }

  listenForSessionAccess() {
    this.sessionAccessSubscription = this.webSocketService.getMessages().subscribe(
      (message: any) => {
        if (message.data === true) { 
          this.isAuthenticated = true;
        }
      },
      (error: any) => {
        console.error('Error receiving session access:', error);
      }
    );
  }

  decryptPassword(encryptedPassword: string): string {
    const bytes = CryptoJS.AES.decrypt(encryptedPassword, this.secretKey);
    return bytes.toString(CryptoJS.enc.Utf8);
  }

  submitPassword() {
    if (!this.enteredPassword) {
      console.error("Password field is empty!");
      return;
    }

    const decryptedCorrectPassword = this.decryptPassword(this.correctPassword);
    if (this.enteredPassword === decryptedCorrectPassword) {
      this.webSocketService.sendMessageToFlask(`{"Name": "SessionAccess"}`);
    } else {
      console.error("Incorrect password entered.");
    }
  }

  @HostListener('window:beforeunload', ['$event'])
  handleUnload(event: Event) {
    if (this.isAuthenticated) {
      this.logout();
    }
    event.preventDefault();
  }

  logout() {
    this.isAuthenticated = false;
    this.webSocketService.sendMessageToFlask(`{"Name": "SessionEnd"}`);
  }
}
