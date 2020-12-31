import { IonButton,
         IonContent,
         IonIcon,
         IonLabel,
         IonNote,
         IonPage,
       } from '@ionic/react';
import React, { useState } from 'react';
import { RouteComponentProps } from 'react-router-dom'
import './Home.css';
import { image, receiptSharp } from 'ionicons/icons';

const Home: React.FC<RouteComponentProps> = (props) => {
  const inputPhotoRef = React.useRef<HTMLInputElement>(null);
  const handleClickPhoto = () => {
    if(inputPhotoRef && inputPhotoRef.current) {
      inputPhotoRef.current.click();
    }
  }

  const [photoData, setPhotoData] = useState<File | null>(null);
  const [photoName, setPhotoName] = useState("No Photo chosen");
  const handleChangePhoto = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files;
    if (file !== null && file[0] !== null) {
      console.log(file[0])
      const fName = file[0].name;
      setPhotoData(file[0]);
      setPhotoName(fName);
    }
  }

  return (
    <IonPage>
      <IonContent>
        <div className="centered">
          <div className="home-title">
            <IonNote className="middle-text">Miyata Lab</IonNote><br />
            <IonLabel className="large-text">Tornedge</IonLabel>
          </div>
          <IonIcon icon={receiptSharp} className="huge-icon ion-margin"/>
          <IonButton size="large" strong={true} onClick={() => {props.history.push('/Functions')}}>
          {/*<IonButton size="large" strong={true} onClick={handleClickPhoto}>*/}
            <IonIcon icon={image} className="ion-margin-end" />Choose Photo
            <input className="display-none" type="file" ref={inputPhotoRef} accept="image/*" onChange={handleChangePhoto}/>
          </IonButton>
          <IonLabel className="ion-margin">{photoName}</IonLabel>
        </div>
      </IonContent>
    </IonPage>
  );
};

export default Home;
