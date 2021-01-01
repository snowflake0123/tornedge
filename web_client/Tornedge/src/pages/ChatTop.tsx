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
import { generateFormData } from '../generateFormData';

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

    const formData = generateFormData(
      'cmd', 'create_chat_room',
      'image_id', localStorage.getItem('image_id')
    );

    // Send data using axios
    axios.post('http://localhost:56060', formData).then((response) => {
      localStorage.chat_room_id = response.data.data.chat_room_id;
    })
    .catch((error) => {
      console.log(error);
    });
    props.history.push('/chatRoom');
  }

  const handleClickEnterRoom = () => {
    console.log('[API] enter_chat_room');

    const formData = generateFormData(
      'cmd', 'chat_room_id',
      'image_id', localStorage.getItem('image_id')
    );

    axios.post('http://localhost:56060', formData).then((response) => {
      localStorage.chat_room_id = response.data.data.chat_room_id;
    })
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