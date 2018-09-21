'use strict';

import { ClipLoader } from 'react-spinners';

class LoadingSpinner extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            loading: true
        }
    }
    render(){
        return (
            <div className='sweet-loading'>
                <ClipLoader
                    sizeUnit={"px"}
                    size={150}
                    color={'#123abc'}
                    loading={this.state.loading}
                    />
            </div>
        )
    }
}
const domContainer = document.querySelector('#overlay_spinner_container');
ReactDOM.render(e(LoadingSpinner), domContainer);