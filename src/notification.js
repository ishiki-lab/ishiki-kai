import React, { PureComponent } from 'react';
import './notification.css';


export class Notification extends PureComponent {
  
  constructor(props) {
    super(props);

    this.state = {
      timer: null,
      isActive: false,
      message: '',
    }
  }

  //Takes message param and sets notification state to active for 8s. Then resets state.
  openNotification = (message) => {
    this.setState({ 
      isActive: true,
      message: message
    })
    this.timer = window.setTimeout(() => {
      this.setState({
        isActive: false,
        message: ''
      });
    }, 6000);
  }  

  render() {
    if(this.state.isActive) {
      return (
        <div className="notification">
          <div className="notification-body" >
            {this.state.message}
          </div>
        </div>
      )
    } else {
      return null
    }
  }
}