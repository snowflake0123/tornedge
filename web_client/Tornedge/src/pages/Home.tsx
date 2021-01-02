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
  const handleChangePhoto = (event: React.ChangeEvent<HTMLInputElement>) => {
    console.log('[API] upload_image');
    const file = event.target.files;
    let fName = "No photo chosen";
    if (file !== null && file[0] !== (null || undefined)) {
      fName = file[0].name;
      // TODO:
      // Client: FormDataを作り，サーバへPOSTリクエストを送る
      //// const formData = generateFormData(1,"hello",3,"hogehoge");
      // Server: 紙片画像から特徴量抽出してDBに登録する
      // Client: サーバから image_id を受け取って LocalStorage に保存する
      //// setImageID(image_id)
      const formData = generateFormData(
        'cmd', 'upload_image',
        'image', file[0]
      )
      axios.post('http://localhost:56060', formData).then((response) => {
        // localStorage.image_id = response.data.data.image_id;
        // console.log('localstorage', localStorage.getItem('image_id'));
        setImageID(response.data['data']['image_id']);
        console.log('localstorage', imageID);
        // props.history.push('/Functions');
      })
      .catch((error) => {
        console.log(error);
      });
      props.history.push('/Functions');
    }
    console.log(fName);
    setPhotoName(fName);
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
          <IonButton size="large" strong={true} onClick={handleClickPhoto}>
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
