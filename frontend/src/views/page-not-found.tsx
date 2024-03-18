import React from 'react';
import { pageNotFound } from '../lib/constants';
const PageNotFound: React.FC = () => {
    return (
        <div className="rounded-2xl p-5 m-5 flex flex-col items-center align-middle justify-center">
            <img
                src={pageNotFound}
                className="max-w-[600px] max-h-[600px] rounded-2xl"
                alt=""
            />
        </div>
    );
};

export default PageNotFound;