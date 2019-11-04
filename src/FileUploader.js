import React from 'react';
import './index.css';
import { Notification } from './notification';

class FileUploader extends React.Component {

    //Ref for notification component
    notificationRef = React.createRef()

    constructor(props) {
        super(props);

        this.state = {
            selectedFile: null,
            selectedCol: '#011993',
        }
        this.fileChangeHandler = this.fileChangeHandler.bind(this)
        this.handleSubmit = this.handleSubmit.bind(this)
        this.colorChangeHandler = this.colorChangeHandler.bind(this)
        this.distanceHandlerActive = this.distanceHandlerActive.bind(this)
        this.distanceHandlerDeactive = this.distanceHandlerDeactive.bind(this)
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
            this.notificationManager("Success: Audio and Colour Uploaded")
        } else if (!fileresponse && colresponse) {
            this.notificationManager("Error: Failed to upload audio file")
        } else if (fileresponse && !colresponse) {
            this.notificationManager("Error: Failed to upload colour")
        } else if (!fileresponse && !colresponse) {
            this.notificationManager("Error: Upload failed")
        }

    }

    distanceHandlerActive = () => {
        //Run temp test for distance sensor active
        if(this.endpointRequest(true)){
            this.notificationManager("Success: Activated")
        } else {
            this.notificationManager("Error: Could not activate")
        }
    }

    distanceHandlerDeactive = () => {
        //Run temp test for distance sensor deactive
        if(this.endpointRequest(false)){
            this.notificationManager("Success: Deactivated")
        } else {
            this.notificationManager("Error: Could not deactivate")
        }
    }

    //End point requests for dummy distance sensor
    endpointRequest = async (state) => {
        var url = ''
        if(state){
            url = 'http://192.168.0.56:5000/start-test'
        } else {
            url = 'http://192.168.0.56:5000/test-kill'
        } 
        if(url !== '')
            var data = {
                "active": state
            }
            const response = await fetch(url, {
                method: 'POST',
                body: JSON.stringify(data)
            }).catch((error) => {
                console.log("Sensor Response Error: ", error)
            });
            if(response.response === 200)
                return true
            
        return false
        
    }
    

    //POST file input form data
    uploadFile = async (data) => {
        let url = 'http://192.168.0.56:5000/uploadfile'
        const response = await fetch(url, {
            method: 'POST',
            body: data,
        })
        if(response.response === 200){
            return true
        } else {
            console.log("Upload File Error: ", response)
            return false
        }

    }

    //POST col value form data
    uploadCol = async (selectedCol) => {
        let url = 'http://192.168.0.56:5000/uploadcol';
        const response = await fetch(url, {
            method: 'POST',
            body: selectedCol,
        })
        if(response.response === 200){
            return true
        } else {
            console.log("Upload File Error: ", response)
            return false
        }
    }

    //Inits timed notification component with message param
    notificationManager(message){
        this.notificationRef.current.openNotification(message)
    }

    render() {
        return (
            <div className="form_body">
                <form onSubmit={this.handleSubmit}> 
                    <label>Select Music File</label><br />
                    <input type="file" id="fileinput" name="file" accept=".mp3,.mp4;" onChange={this.fileChangeHandler}/><br />
                    <label>Select Colour</label><br /><br />
                    <input type="color" name="colour" onChange={this.colorChangeHandler} value={this.state.selectedCol}/> <br />
                    <input type="submit" value="Upload" className="inputbtn"/>  
                </form>
                <br />
                <button className="tempSensorBtn" onClick={this.distanceHandlerActive} > ACTIVATE SENSOR</button>
                <button className="tempSensorBtn" onClick={this.distanceHandlerDeactive} > DEACTIVATE SENSOR</button>
                <br />
                <Notification ref = {this.notificationRef} />
            </div>
        )
    }

}

export default FileUploader;