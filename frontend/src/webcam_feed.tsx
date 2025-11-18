
import React, { useRef, useEffect } from 'react';

const WebcamFeed = () => {
  const videoRef = useRef<HTMLVideoElement>(null);

  useEffect(() => {
    navigator.mediaDevices.getUserMedia({ video: true })
      .then(stream => {
        if (videoRef.current) {
          videoRef.current.srcObject = stream;
        }
      })
      .catch(err => console.error("Webcam error", err));
  }, []);

  return <video ref={videoRef} autoPlay playsInline width={200} height={100} />;
};

export default WebcamFeed;
