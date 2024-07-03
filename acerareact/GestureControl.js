import React, { useEffect, useRef } from 'react';

const GestureControl = () => {
    const videoRef = useRef(null);

    useEffect(() => {
        const hands = new window.Hands({ locateFile: (file) => `https://cdn.jsdelivr.net/npm/@mediapipe/hands/${file}` });
        hands.setOptions({
            maxNumHands: 1,
            modelComplexity: 1,
            minDetectionConfidence: 0.5,
            minTrackingConfidence: 0.5
        });

        hands.onResults(onResults);

        const camera = new window.Camera(videoRef.current, {
            onFrame: async () => {
                await hands.send({ image: videoRef.current });
            },
            width: 640,
            height: 480
        });
        camera.start();

        function onResults(results) {
            if (!results.multiHandLandmarks) return;
            // Handle hand landmarks
            console.log(results.multiHandLandmarks);
        }
    }, []);

    return <video ref={videoRef} style={{ display: 'none' }} />;
};

export default GestureControl;
