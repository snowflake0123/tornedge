import {
  IonBackButton,
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

import axios from 'axios';
import { generateFormData } from '../generateFormData';

const ChatTop: React.FC<RouteComponentProps> = (props) => {
  const [showToast, setShowToast] = useState(false);
  const [errorMessage, setErrorMessage] = useState('');

  const handleClickCreateChatRoom = () => {
   /* Functions
    *   1: Send request
    *   2: Save chat_room_id to localStrorage
    *   3: move to ChatRoom page
    */
    console.log('[API] create_chat_room');

    // 1: Send request
    if (localStorage.getItem('chat_room_id')) {
      props.history.push('/chatRoom');
    } else {
      const formData = generateFormData(
        'cmd', 'create_chat_room',
        'image_id', localStorage.getItem('image_id')
      );
      axios.post('http://localhost:56060', formData).then((response) => {
        // 2: Save chat_room_id
        const res_data = response.data['data'];
        console.log(response)
        if(res_data['result'] === 'success') {
          localStorage.chat_room_id = res_data['chat_room_id'];
          console.log('chat_room_id', localStorage.getItem('chat_room_id'))
          props.history.push('/chatRoom');
        } else {
          setErrorMessage('Failed to create the chat room');
          setShowToast(true);
        }
      })
      .catch((error) => {
        setErrorMessage('Failed to create the chat room')
        setShowToast(true)
        console.log(error);
      });
    }
  }

  const handleClickEnterChatRoom = () => {
   /* Functions
    *   1: Send request
    *   2: Save chat_room_id to localStrorage
    */
    if(localStorage.getItem('chat_room_id')) {
      props.history.push('/chatRoom');
    } else {
      console.log('[API] enter_chat_room');

      // 1: Send request
      const formData = generateFormData(
        'cmd', 'enter_chat_room',
        'image_id', localStorage.getItem('image_id')
      );
      axios.post('http://localhost:56060', formData).then((response) => {
        // 2: Save chat_room_id to localStorage
        const res_data = response.data['data'];
        if(res_data['result'] === 'success') {
          localStorage.chat_room_id = res_data['chat_room_id'];
          console.log('chat_room_id', localStorage.getItem('chat_room_id'))
          props.history.push('/chatRoom');
        } else {
          setErrorMessage('Failed to enter the chat room');
          setShowToast(true);
        }
      })
      .catch((response) => {
        setErrorMessage('Failed to enter the chat room');
        setShowToast(true);
      });
    }
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
          position="middle"
          color="danger"
          onDidDismiss={() => setShowToast(false)}
          message={errorMessage}
          duration={5000}
        />
      </IonContent>
    </IonPage>
  );
};
export default ChatTop;
