import { IonButton,
         IonContent,
         IonIcon,
         IonLabel,
         IonLoading,
         IonNote,
         IonPage,
         IonProgressBar,
         IonToast,
         useIonViewWillLeave
       } from '@ionic/react';
import React, { useState } from 'react';
import { RouteComponentProps } from 'react-router-dom'
import './Home.css';
import { image, receiptSharp } from 'ionicons/icons';
import useLocalStorage from './../hooks/useLocalStorage'
import { generateFormData } from './../generateFormData'
import axios from 'axios';

const Home: React.FC<RouteComponentProps> = (props) => {
  const inputPhotoRef = React.useRef<HTMLInputElement>(null);
  const handleClickPhoto = () => {
    if(inputPhotoRef && inputPhotoRef.current) {
      inputPhotoRef.current.click();
    }
  }

  const [imageID, setImageID] = useLocalStorage<String | null>('image_id', null);
  const [photoName, setPhotoName] = useState("No photo chosen");
  const [showLoading, setShowLoading] = useState(false);
  const [showProgressBar, setShowProgressBar] = useState(false);
  const [showSuccessToast, setShowSuccessToast] = useState(false);
  const [showFailureToast, setShowFailureToast] = useState(false);
  const handleChangePhoto = (event: React.ChangeEvent<HTMLInputElement>) => {
    console.log('[API] upload_image');
    const file = event.target.files;
    let fName = "No photo chosen";
    if (file !== null && file[0] !== (null || undefined)) {
      fName = file[0].name;
      const formData = generateFormData(
        'cmd', 'upload_image',
        'image', file[0]
      )
      setShowLoading(true);
      setShowProgressBar(true);
      axios.post('http://localhost:56060', formData).then((response) => {
        localStorage.clear();
        setImageID(response.data['data']['image_id']);
        console.log('localstorage', imageID);
        setShowSuccessToast(true);
        props.history.push('/Functions');
      })
      .catch((error) => {
        setShowProgressBar(false);
        setShowLoading(false);
        setShowFailureToast(true);
        console.log(error);
      });
      // props.history.push('/Functions');
    }
    console.log(fName);
    setPhotoName(fName);
  }

  useIonViewWillLeave(() => {
    setShowProgressBar(false);
    setShowLoading(false);
    setShowFailureToast(false);
  });

  return (
    <IonPage>
      <IonContent>
        <div className="centered">
          <div className="home-title">
            <IonNote className="middle-text">Miyata Lab</IonNote><br />
            <IonLabel className="large-text">Tornedge</IonLabel>
          </div>
          <IonIcon icon={receiptSharp} className="huge-icon ion-margin"/>
          <IonButton size="large" strong={true} onClick={handleClickPhoto}>
            <IonIcon icon={image} className="ion-margin-end" />Choose Photo
            <input className="display-none" type="file" ref={inputPhotoRef} accept="image/*" onChange={handleChangePhoto}/>
          </IonButton>
          <IonLabel className="ion-margin">{photoName}</IonLabel>
          <IonProgressBar type="indeterminate" style={{ display: showProgressBar ? '' : 'none' }}></IonProgressBar>
        </div>

        <IonLoading
          isOpen={showLoading}
          message={'Uploading...'}
        />
        <IonToast
          isOpen={showSuccessToast}
          color="primary"
          onDidDismiss={() => setShowSuccessToast(false)}
          message="Image Upload Succeeded."
          position="bottom"
          duration={2500}
        />
        <IonToast
          isOpen={showFailureToast}
          color="danger"
          onDidDismiss={() => setShowFailureToast(false)}
          message="Image Upload Failed."
          position="bottom"
          duration={2500}
        />
      </IonContent>
    </IonPage>
  );
};

export default Home;
