import React from 'react';
import TestButton from './components/TestButton';
import './index.css';

let API_URL = process.env.REACT_APP_STAGE === 'dev' ? "http://192.168.0.56:5000" : window.location.origin;

class FileUploader extends React.Component {

    constructor(props) {
        super(props);

        this.state = {
            selectedFile: null,
            selectedCol: '#011993',
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
        this.uploadFile(data)
        this.uploadCol(data)
    }

    //POST file input form data
    uploadFile(data) {

        const url = API_URL + '/upload-file'
        fetch(url, {
            method: 'POST',
            body: data,
        })
        .catch(error => console.log(error)
        );
    }

    //POST col value form data
    uploadCol(selectedCol) {
        const url = API_URL + '/upload-colour';
        fetch(url, {
            method: 'POST',
            body: selectedCol,
        })
        .catch(error => console.log(error)
        );
    }

    render() {
        return (
            <>
                <div className="form_body">
                    <form onSubmit={this.handleSubmit}> 
                        <label>Select Music File</label><br />
                        <input type="file" id="fileinput" name="file" accept=".mp3,.mp4;" onChange={this.fileChangeHandler}/><br />
                        <label>Select Colour</label><br /><br />
                        <input type="color" name="colour" onChange={this.colorChangeHandler} value={this.state.selectedCol}/> <br />
                        <input type="submit" value="Upload" className="inputbtn"/>  
                    </form>
                    <div className="test-button">
                        <TestButton 
                            endpoint={API_URL}
                        />
                    </div>
                </div>

            </>
        )
    }

}

export default FileUploader;