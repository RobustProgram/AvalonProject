import React from 'react';
import ReactDOM from 'react-dom';
import UIkit from 'uikit';
import Icons from 'uikit/dist/js/uikit-icons';

import App from './App';
import * as serviceWorker from './serviceWorker';

import 'react-toastify/dist/ReactToastify.css';
import 'uikit/dist/css/uikit.min.css';

UIkit.use(Icons);

ReactDOM.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
  document.getElementById('root')
);

// If you want your app to work offline and load faster, you can change
// unregister() to register() below. Note this comes with some pitfalls.
// Learn more about service workers: https://bit.ly/CRA-PWA
serviceWorker.unregister();
