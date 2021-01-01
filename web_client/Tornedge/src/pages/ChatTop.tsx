import {
  IonBackButton,
  IonButton,
  IonButtons,
  IonContent,
  IonHeader,
  IonIcon,
  IonPage,
  IonTitle,
  IonToolbar
} from '@ionic/react';
import React from 'react';
import { RouteComponentProps } from 'react-router-dom'
import './ChatTop.css';
import { receiptSharp, image } from 'ionicons/icons';

import axios, { AxiosResponse } from 'axios';

const ChatTop: React.FC<RouteComponentProps> = (props) => {
  const url: string = "localhost:56060";

  const inputPhotoRef = React.useRef<HTMLInputElement>(null);
  const handleClickPhoto = () => {
    if(inputPhotoRef && inputPhotoRef.current) {
      inputPhotoRef.current.click();
    }
  }

  const handleClickCreateCRoom = (url: string) => {
    console.log('[API] create_chat_room')
    const formData = new FormData();
    formData.append('cmd', 'create_chat_room');
    formData.append('image_id', '1');

    // Send data using axios
    axios.post(url, formData).then((response) => {
      console.log(response);
    })
    .catch((error) => {
      console.log(error);
    });
    props.history.push('/chatRoom');
  }

  const handleClickEnterRoom = () => {
    props.history.push('/chatRoom');
  }

  return (
    <IonPage>
      {/* Header */}
      <IonHeader>
        <IonToolbar>
          <IonButtons slot="start">
            <IonBackButton defaultHref="/functions" />
          </IonButtons>
          <IonTitle>Chat</IonTitle>
        </IonToolbar>
      </IonHeader>

      {/* Content */}
      <IonContent>
        <div className="centered">
          {/* Icon */}
          <IonIcon icon={receiptSharp} className="huge-icon ion-margin-bottom"/>

          {/* Create Room Button */}
          <IonButton size="large" strong={true} onClick={() => {
            props.history.push('/chatRoom')
          }}>
            <IonIcon icon={image} className="ion-margin-end" />Create Room
            <input className="display-none" type="file" ref={inputPhotoRef} accept="image/*" />
          </IonButton>

          {/* Enter Room Button */}
          <IonButton size="large" strong={true} onClick={() => {
            props.history.push('/chatRoom')
          }}>
            <IonIcon icon={image} className="ion-margin-end" />Enter Room
            <input className="display-none" type="file" ref={inputPhotoRef} accept="image/*" />
          </IonButton>
        </div>
      </IonContent>
    </IonPage>
  );
};
export default ChatTop;