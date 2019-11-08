import React from 'react';
import './TestButton.css';
import '../index.css';

const testStates = {
    TEST_START : 0,
    TEST_IN_PROGRESS : 1,
    TEST_KILL : 2
}

class Reboot extends React.Component {

    triggerReboot = () => {
        const url = this.props.endpoint + '/reboot';
        this.props.notificationManager.current.openNotification("Reboot has been started, please wait 5 minutes");
        fetch(url, {
            method: 'GET'
        }).then(() => {
            console.log('reboot doesn\'t return anything, you should never be here!');  
        })
        .catch(error => this.props.notificationManager.current.openNotification("Reboot is still in progress")
        );
    }

    render() {
        return (
            <>
                <button 
                    onTouchStart={() => this.triggerReboot()}
                    onTouchEnd={() => this.triggerReboot()}
                    onMouseDown={() => this.triggerReboot()}
                    onMouseUp={() => this.triggerReboot()}
                    className="inputbtn">
                    Emergency reboot 
                </button>
            </>
        )
    }

}

export default Reboot;