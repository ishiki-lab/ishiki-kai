import React from 'react';
import ReactDOM from 'react-dom';
import './index.css';
import * as serviceWorker from './serviceWorker';

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
        uploadFile(data)
        uploadCol(data)
    }

    render() {
        return (
            <div className="form_body">
                <form onSubmit={this.handleSubmit}> 
                    <label>Select Music File</label>
                    <input type="file" id="fileinput" name="file" id="file_btn" accept=".mp3,.mp4;" onChange={this.fileChangeHandler}/>
                    <label>Select Colour</label><br /><br />
                    <input type="color" name="colour" onChange={this.colorChangeHandler} value={this.state.selectedCol}/> <br />
                    <input type="submit" value="Upload" id="inputbtn"/>  
                </form>
            </div>
        )
    }
}

//POST file input form data
function uploadFile(data) {

    const url = 'http://127.0.0.1:5000/uploadfile';
     fetch(url, {
       method: 'POST',
       body: data,
      })
      .then(success => {
        console.log("Upload File Success: " + success)
      })
      .catch(error => console.log(error)
    );
}

//POST col value form data
function uploadCol(selectedCol) {
  
    const url = 'http://127.0.0.1:5000/uploadcol';
    fetch(url, {
        method: 'POST',
        body: selectedCol,
       })
       .then(success => {
            console.log("Upload Hex Success: " + success)
       })
       .catch(error => console.log(error)
     );
}

class App extends React.Component {
   
    render() {
      return (
        <div>
          <div className = "layout_header">
            <h1>File uploader</h1>
          </div>
          {<FileUploader />}
        </div>
      )
    }
  }


ReactDOM.render(<App />, document.getElementById('root'));
serviceWorker.unregister();
