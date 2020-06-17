/**
 * application index file
 * 
 * @author    Maurizio Tidei
 * @copyright © 2018 contexagon GmbH
 *
 * @license
 * This file is part of MusOS and is released under the GPLv3 license.
 * Please see the LICENSE.md file that should have been included
 * as part of this package.
 */


import React from 'react';
import ReactDOM from 'react-dom';
import './index.css';
import App from './components/application/App';
import registerServiceWorker from './registerServiceWorker';


function isIE() {
  const ua = navigator.userAgent;
  return ua.indexOf("MSIE ") > -1 || ua.indexOf("Trident/") > -1;
}

if (isIE()){
    alert('Internet Explorer is currently not supported by musOS. Please use Edge, Chrome, Firefox, Opera or Safari.');
}

ReactDOM.render(<App />, document.getElementById('root'));
registerServiceWorker();
