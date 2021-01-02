import {
  IonBackButton,
  IonButton,
  IonButtons,
  IonCard,
  IonCardHeader,
  IonCardTitle,
  IonCardContent,
  IonContent,
  IonHeader,
  IonIcon,
  IonPage,
  IonTitle,
  IonToolbar,
  IonToast
} from '@ionic/react';
import React, { useState } from 'react';
import { RouteComponentProps } from 'react-router-dom'
import './ChatTop.css';
import { addCircle, enter } from 'ionicons/icons';

import axios, { AxiosResponse } from 'axios';
import { generateFormData } from '../generateFormData';
import { Cipher } from 'crypto';

const ChatTop: React.FC<RouteComponentProps> = (props) => {
  const [showToast, setShowToast] = useState(false);
  const [errorMessage, setErrorMessage] = useState('');

  const inputPhotoRef = React.useRef<HTMLInputElement>(null);
  const handleClickPhoto = () => {
    if(inputPhotoRef && inputPhotoRef.current) {
      inputPhotoRef.current.click();
    }
  }

  const handleClickCreateChatRoom = () => {
   /* Functions
    *   1: Send request
    *   2: Save chat_room_id to localStrorage
    *   3: move to ChatRoom page
    */
    console.log('[API] create_chat_room');

    // 1: Send request
    if(localStorage.getItem('image_id') !== null) {
      const formData = generateFormData(
        'cmd', 'create_chat_room',
        'image_id', localStorage.getItem('image_id')
      );
      axios.post('http://localhost:56060', formData).then((response) => {
        // 2: Save chat_room_id 
        const res_data = response.data;
        console.log(response)
        if(res_data['result'] === 'success') {
          localStorage.chat_room_id = res_data['chat_room_id'];
          console.log('chat_room_id', localStorage.getItem('chat_room_id'))
        } else {
          console.log('e')
          setErrorMessage(res_data['message']);
          setShowToast(true);
        }
      })
      .catch((error) => {
        console.log(error);
      });
    }
    // 3: move ot ChatRoom page
    props.history.push('/chatRoom');
  }

  const handleClickEnterChatRoom = () => {
   /* Functions
    *   1: Send request
    *   2: Save chat_room_id to localStrorage
    */
    console.log('[API] enter_chat_room');

    // 1: Send request
    const formData = generateFormData(
      'cmd', 'chat_room_id',
      'image_id', localStorage.getItem('image_id')
    );
    axios.post('http://localhost:56060', formData).then((response) => {
      // 2: Save chat_room_id to localStorage
      const res_data = response.data['data'];
      if(res_data['result'] === 'success') {
        localStorage.chat_room_id = res_data['chat_room_id'];
        console.log('chat_room_id', localStorage.getItem('chat_room_id'))
      } else {
        setErrorMessage(res_data['message']);
        setShowToast(true);
      }
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
          <div className="functions">
          {/* Create Room Button */}
          <IonCard className="ion-text-center" onClick={() => handleClickCreateChatRoom()}>
            <IonCardHeader>
              <IonCardTitle>Create Room</IonCardTitle>
            </IonCardHeader>
            <IonCardContent>
              <IonIcon icon={addCircle} className="larger-icon" />
            </IonCardContent>
          </IonCard>

          {/* Enter Room Button */}
          <IonCard className="ion-text-center" onClick={() => handleClickEnterChatRoom()}>
            <IonCardHeader>
              <IonCardTitle>Enter Room</IonCardTitle>
            </IonCardHeader>
            <IonCardContent>
              <IonIcon icon={enter} className="larger-icon" />
            </IonCardContent>
          </IonCard>
          </div>
        </div>
        {/* Toast */}
        <IonToast
          isOpen={showToast}
          onDidDismiss={() => setShowToast(false)}
          message={errorMessage}
          duration={200}
        />
      </IonContent>
    </IonPage>
  );
};
export default ChatTop;
