import React from 'react';
import TestButton from './components/TestButton';
import Reboot from './components/Reboot';
import './index.css';
import { Notification } from './notification';

let API_URL = process.env.REACT_APP_STAGE === 'dev' ? "http://192.168.63.202:5000" : window.location.origin;

class FileUploader extends React.Component {

    //Ref for notification component
    notificationRef = React.createRef()

    constructor(props) {
        super(props);

        this.state = {
            selectedFile: null,
            selectedCol: '#011993',
            currentTrack: null,
            hostname: "Offline"
        }
    }

    fileChangeHandler = (event) => {
        let val = event.target.files[0];
        this.setState({selectedFile: val});
    }

    colorChangeHandler = (event) => {
        let val = event.target.value;
        this.setState({selectedCol: val})
    }

    handleSubmit = (event) => {
        event.preventDefault()
        const data = new FormData()
        data.append('file', this.state.selectedFile)
        data.append('colour', this.state.selectedCol)
        
        //Upload methods return boolean success/fail
        let fileresponse = this.uploadFile(data)
        let colresponse = this.uploadCol(data)

        //Calls notification component manager
        if(fileresponse && colresponse) {
            console.log("Response from notification manager: ", fileresponse, colresponse)
            this.notificationManager("Upload success")
        } else if (!fileresponse && !colresponse) {
            console.log("Response from notification manager: ", fileresponse, colresponse)
            this.notificationManager("Error: Failed to upload audio file")
        } else if (!fileresponse && colresponse) {
            this.notificationManager("Error: Failed to upload colour")
        } else if (!fileresponse && !colresponse) {
            this.notificationManager("Error: Upload failed")
        }
    }

    distanceHandlerActive = () => {
        //Run temp test for distance sensor active
        this.notificationManager("Warming up the room...");
        this.endpointRequest(true).then((success) => {
            if (success){
                this.notificationManager("Success: Activated");
            } else {
                this.notificationManager("Error: Could not activate");
            }
        }).catch((e) => {
            console.log("Something went horribly wrong...");
        })
        
    }

    distanceHandlerDeactive = () => {
        //Run temp test for distance sensor deactive
        this.notificationManager("Ending the test...");
        if (this.endpointRequest(false)){
            this.notificationManager("Success: Deactivated");
        } else {
            this.notificationManager("Error: Could not deactivate");
        }
    }

    //End point requests for dummy distance sensor
    endpointRequest = async (state) => {
        console.log('epr: ', state);
        
        
        var url = '';
        if(state){
            url = API_URL + '/test-start';
        } else {
            url = API_URL + '/test-kill';
        } 

        if(url !== '') {

            const res = await fetch(url, {
                headers: {'Content-Type': 'application/json'}
            })

            const response = await res.json();

            console.log('json res: ', response)
           
            if(response != null && response.response === 200) {
                return true;
            } 
        }
        return false;
    }
    

    //POST file input form data
    uploadFile = async (data) => {
        const url = API_URL + '/upload-file';
        const response = await fetch(url, {
            method: 'POST',
            body: data,
        })
        if(response != null && response.response === 200){
            return true
        }
        return false
    }


    //POST col value form data
    uploadCol = async (selectedCol) => {
        const url = API_URL + '/upload-colour';
        const response = await fetch(url, {
            method: 'POST',
            body: selectedCol,
        })
        if(response != null && response.response === 200){
            return true
        }
        return false
    }

    //Inits timed notification component with message param
    notificationManager(message){
        this.notificationRef.current.openNotification(message)
    }

    // Get what's loaded onto the scentroom right now

    async componentDidMount() {
        const url = API_URL + '/status';
        const res = await fetch(url, {
            headers: {'Content-Type': 'application/json'}
        })

        const response = await res.json();

        if (response.response === 200 && response.status === "healthy" && response.color) {
            this.setState({
                selectedCol: response.color,
                currentTrack: response.track_name,
                hostname: response.hostname
            })
        }

        console.log('json res: ', response)

    }

    render() {
        return (
            <>
                <div className = "layout_header">
                    <h1>{this.state.hostname}</h1>
                </div>
                <div className="form_body">
                    <form onSubmit={this.handleSubmit}> 
                        {this.state.currentTrack ? (
                            <>
                                <h4>is loaded with:</h4>
                                <h2 id="track-name">{this.state.currentTrack}</h2>
                            </>
                        ) : (
                            <h5>No track found on this scentroom</h5>
                        )}
                        <label>Upload a new mp3 from your device</label><br />
                        <input type="file" id="fileinput" name="file" accept=".mp3" onChange={this.fileChangeHandler}/>
                        <label>Pick a color</label><br /><br />
                        <input type="color" name="colour" onChange={this.colorChangeHandler} value={this.state.selectedCol}/> <br />
                        <input type="submit" value="Upload" className="inputbtn"/>  
                    </form>
                    <hr/>
                    <div className="test-button">
                        <TestButton 
                            endpoint={API_URL}
                            notificationManager={this.notificationRef}
                        />
                    </div>
                    or...
                    <br />
                    <button className="tempSensorBtn" onClick={this.distanceHandlerActive} > Start test</button>
                    <button className="tempSensorBtn" onClick={this.distanceHandlerDeactive} > End test</button>
                    <br />
                    <br/>
                    <Notification ref = {this.notificationRef} />
                    <hr/>
                    <Reboot 
                        endpoint={API_URL}
                        notificationManager={this.notificationRef}
                    />
                </div>
            </>
        )
    }
}

export default FileUploader;