import {
  IonButton,
  IonButtons,
  IonContent,
  IonHeader,
  IonIcon,
  IonItem,
  IonLabel,
  IonList,
  IonPage,
  IonRefresher,
  IonRefresherContent,
  IonTitle,
  IonToolbar,
  useIonViewWillEnter,
  IonInput,
  IonToast
} from '@ionic/react';
import React, { useState } from 'react';
import './ChatRoom.css';
import { RefresherEventDetail } from '@ionic/core';
import { arrowDownCircleOutline, reload } from 'ionicons/icons';
import { RouteComponentProps } from 'react-router';
import axios from 'axios';
import { generateFormData } from '../generateFormData';


type Message = {
  image_id: string
  text: string
}

type Messages = {
  messages: Message[]
}

const initMessages: Message[] = []

const MyMsg: React.FC<Message> = (props) => {
  return (
    <IonItem lines="none">
      <IonLabel className="ion-margin-start me-speech-bubble ion-padding ion-text-wrap">
        {props.text}
      </IonLabel>
    </IonItem>
  )
}

const PartnerMsg: React.FC<Message> = (props) => {
  return (
    <IonItem lines="none">
      <IonLabel className="ion-margin-end partner-speech-bubble ion-padding ion-text-wrap">
        {props.text}
      </IonLabel>
    </IonItem>
  )
}

const MsgList: React.FC<Messages> = (props) => {
  if (props.messages.length === 0) return null;
  return (
    <IonList className="ion-padding-top">
      { props.messages.map((message: Message, index:number) => {
        if (message.image_id === localStorage.getItem('image_id')) {
          return (<MyMsg key={index} image_id={message.image_id} text={message.text}/>)
        } else {
          return (<PartnerMsg key={index} image_id={message.image_id} text={message.text}/>)
        }
      })}
    </IonList>
  )
}


const ChatRoom: React.FC<RouteComponentProps> = (props) => {
  const [messages, setMessages] = useState(initMessages);
  const [message, setMessage] = useState('');
  const [showToast, setShowToast] = useState(false);
  const [errorMessage, setErrorMessage] = useState('');

  const handleClickBack = () => {
    props.history.goBack();
  }


  const handleClickSend = () => {
   /* Functions
    *   Step1: Send request
    *   Step2: Update chat log value in state
    *   Step3: Reset value of input textarea
    */
    console.log('[API] send_chat');

    // 1: send request
    const new_message = localStorage.getItem('image_id') + ', ' + message
    console.log(new_message)
    const formData = generateFormData(
      'cmd', 'send_chat',
      'message', new_message,
      'chat_room_id', localStorage.getItem('chat_room_id')
    );
    axios.post('http://localhost:56060', formData).then((response) => {
      // 2: update chatlog value in state
      const res_data = response.data['data']
      if(res_data['result'] === 'success') {
        const chat_log:Array<string> = res_data['chat_log']
        const new_log:Array<Message> = []
        chat_log.map((value, index) => {
          const line = value.split(',')
          const obj:Message = {
            'image_id': line[0],
            'text': line[1]
          }
          new_log.push(obj);
        })
        setMessages(new_log);
      } else {
        setErrorMessage(res_data['message']);
        setShowToast(true);
      }
    })
    .catch((error) => {
      setErrorMessage('Failed to send the chat message');
      setShowToast(true);
      console.log(error);
    })
    // 3: Reset value of input textarea
    setMessage('');
  }


  const handleClickUpdate = () => {
   /* Functions
    *   Step1: Send request
    *   Step2: Update chat log value in state
    */
    console.log('[API] update_chat');
    // 1: send request
    const formData = generateFormData(
      'cmd', 'update_chat',
      'chat_room_id', localStorage.getItem('chat_room_id')
    )
    axios.post('http://localhost:56060', formData).then((response) => {
      // 2: update chat log value in state
      const res_data = response.data['data']
      if(res_data['result'] === 'success') {
        const chat_log:Array<string> = res_data['chat_log']
        const new_log:Array<Message> = []
        chat_log.map((value, index) => {
          const line = value.split(',')
          const obj:Message = {
            'image_id': line[0],
            'text': line[1]
          }
          new_log.push(obj);
        })
        setMessages(new_log);
      } else {
        setErrorMessage(res_data['message']);
        setShowToast(true);
      }
    })
    .catch((error) => {
      setErrorMessage('Failed to update the chat log');
      setShowToast(true);
      console.log(error);
    })
  }

  function handlePullRefresher(event: CustomEvent<RefresherEventDetail>) {
    handleClickUpdate();
    event.detail.complete();
  }

  useIonViewWillEnter(() => handleClickUpdate())

  return (
    <IonPage>
      {/* Header */}
      <IonHeader>
        <IonToolbar>
          <IonButtons slot="start">
            <IonButton fill="clear" size="small" onClick={() => handleClickBack()}>Back</IonButton>
          </IonButtons>
          <IonTitle>Chat -Chat Room-</IonTitle>
          {/* Reload Button */}
          <IonButton slot="end" color="midium" size="small" onClick={() => handleClickUpdate()}>
            <IonIcon icon={reload}></IonIcon>
          </IonButton>
        </IonToolbar>
      </IonHeader>

      {/* Chat Space */}
      <IonContent>
        <IonRefresher slot="fixed" onIonRefresh={handlePullRefresher}>
          <IonRefresherContent
            pullingIcon={arrowDownCircleOutline}
            pullingText="Pull to refresh"
            refreshingSpinner="circles"
            refreshingText="Refreshing...">
          </IonRefresherContent>
        </IonRefresher>
        <MsgList messages={messages} />
      </IonContent>

      {/* Input */}
      <IonItem>
        <IonInput
          className="ion-margin-start"
          color="Midium"
          placeholder="Message"
          value={message}
          onIonChange={e => setMessage(e.detail.value!)}
          required
          >
        </IonInput>
      </IonItem>
      <div className="ion-padding">
        <IonButton className="send-button" expand="block" onClick={() => handleClickSend()}>Send</IonButton>
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

    </IonPage>
  );
};
export default ChatRoom;
