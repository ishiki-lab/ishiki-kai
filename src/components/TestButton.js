import React from 'react';
import './TestButton.css';
import '../index.css';

const testStates = {
    TEST_START : 0,
    TEST_IN_PROGRESS : 1,
    TEST_KILL : 2
}

class TestButton extends React.Component {

    state = {
        runTest: false
    }

    sendCommand = (c) => {
        if (c === testStates.TEST_START) {
            this.props.notificationManager.current.openNotification("The test is warming up...");
            const url = this.props.endpoint + '/test-start';
            fetch(url, {
                method: 'GET'
            }).then(() => {
                this.props.notificationManager.current.openNotification("Test is running!");   
            })
            .catch(error => console.log(error)
            );
            this.setState({
                runTest: true
            });
        } else if (c === testStates.TEST_KILL) {
            const url = this.props.endpoint + '/test-kill';
            fetch(url, {
                method: 'GET'
            }).then(() => {
                this.props.notificationManager.current.openNotification("Test cancelled");     
            })
            .catch(error => console.log(error)
            );  
            this.setState({
                runTest: false
            }); 
        }
    }

    triggerTest = (s) => {
        if (s === testStates.TEST_START) {
            console.log('Test running!'); 
            this.sendCommand(s); 
        } else if (s === testStates.TEST_KILL) {
            console.log('End of test...');
            this.sendCommand(s); 
        }
    }

    render() {
        return (
            <>
                <button className="red-button"
                    onTouchStart={() => this.triggerTest(testStates.TEST_START)}
                    onTouchEnd={() => this.triggerTest(testStates.TEST_KILL)}
                    onMouseDown={() => this.triggerTest(testStates.TEST_START)}
                    onMouseUp={() => this.triggerTest(testStates.TEST_KILL)}
                    className="inputbtn">
                    { !this.state.runTest ? (
                        <span>Press + hold to test</span>
                    ) : (
                        <span>Release to end</span>
                    )}
                    
                </button>
            </>
        )
    }

}

export default TestButton;