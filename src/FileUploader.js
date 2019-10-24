import React from 'react';
import './index.css';

class FileUploader extends React.Component {

    constructor(props) {
        super(props);

        this.state = {
            selectedFile: null,
            selectedCol: '#011993',
        }
        this.fileChangeHandler = this.fileChangeHandler.bind(this)
        this.handleSubmit = this.handleSubmit.bind(this)
        this.colorChangeHandler = this.colorChangeHandler.bind(this)
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
        this.uploadFile(data)
        this.uploadCol(data)
    }

    render() {
        return (
            <div className="form_body">
                <form onSubmit={this.handleSubmit}> 
                    <label>Select Music File</label><br />
                    <input type="file" id="fileinput" name="file" accept=".mp3,.mp4;" onChange={this.fileChangeHandler}/><br />
                    <label>Select Colour</label><br /><br />
                    <input type="color" name="colour" onChange={this.colorChangeHandler} value={this.state.selectedCol}/> <br />
                    <input type="submit" value="Upload" id="inputbtn"/>  
                </form>
            </div>
        )
    }

    //POST file input form data
    uploadFile(data) {

        const url = window.location.origin + '/uploadfile'
        fetch(url, {
            method: 'POST',
            body: data,
        })
        .catch(error => console.log(error)
        );
    }

    //POST col value form data
    uploadCol(selectedCol) {
    
        const url = window.location.origin + '/uploadcol';
        fetch(url, {
            method: 'POST',
            body: selectedCol,
        })
        .catch(error => console.log(error)
        );
    }
}

export default FileUploader;