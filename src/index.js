import React from 'react';
import ReactDOM from 'react-dom';
import './index.css';
import * as serviceWorker from './serviceWorker';
import FileUploader from './FileUploader'

class App extends React.Component {
   
    render() {
      return (
        <div>
          <div className = "layout_header">
            <h1>ScentRoom Uploader</h1>
          </div>
          {<FileUploader />}
        </div>
      )
    }
  }


ReactDOM.render(<App />, document.getElementById('root'));
serviceWorker.unregister();
