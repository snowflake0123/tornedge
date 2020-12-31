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
  IonItem,
  IonItemOption,
  IonItemOptions,
  IonItemSliding,
  IonLabel,
  IonList,
  IonListHeader,
  IonPage,
  IonTitle,
  IonToolbar
} from '@ionic/react';
import React from 'react';
import './FileReceive.css';
import { images } from 'ionicons/icons';
import { useForm } from 'react-hook-form';
import axios from 'axios';

type Inputs = {
  type: string;
  receipt: FileList;
};

const ReceivedFile: React.FC = () => {
  return (
    <IonItemSliding>
      <IonItem href="https://www.google.com">
        <IonLabel>Item</IonLabel>
      </IonItem>
      <IonItemOptions side="end">
        <IonItemOption color="danger" onClick={() => {}}>Delete</IonItemOption>
      </IonItemOptions>
    </IonItemSliding>
  )
}

const FileReceive: React.FC = () => {
  const { register, setValue, handleSubmit } = useForm<Inputs>();

  const onSubmit = (data: Inputs) => {
    const formData = new FormData();
    formData.set('type', data.type);
    formData.set('receipt', data.receipt[0]);
    formData.set('image', '');

    axios.post("http://localhost:56060/", formData).then(response => {
      console.log('body:', response.data);
    });
  };

  const setTypeReceiver = () => {
    setValue("type", "receiver");
  }

  return (
    <IonPage>
      <IonHeader>
        <IonToolbar>
          <IonButtons slot="start">
            <IonBackButton defaultHref="/FileTop" />
          </IonButtons>
          <IonTitle>File -Receive-</IonTitle>
        </IonToolbar>
      </IonHeader>
      <IonContent>
        <form onSubmit={handleSubmit(onSubmit)}>
          <input name="type" className="display-none" type="text" ref={register} />
          {/*<IonCard>
            <IonCardHeader>
              <IonCardTitle>A Piece of Paper</IonCardTitle>
            </IonCardHeader>
            <IonCardContent>
              <label className="choose-button" onClick={setTypeReceiver}>
                <IonIcon icon={images} className="ion-margin-end" />Choose Photo
                <input name="receipt" className="display-none" type="file" ref={register({required: true})} accept="image/*" />
              </label>
            </IonCardContent>
          </IonCard>*/}
          <IonList>
            <IonListHeader>
              <IonLabel>Received Files</IonLabel>
            </IonListHeader>
            <IonItemSliding>
              <IonItem href="https://www.google.com">
                <IonLabel>Item</IonLabel>
              </IonItem>
              <IonItemOptions side="end">
                <IonItemOption color="danger" onClick={() => {}}>Delete</IonItemOption>
              </IonItemOptions>
            </IonItemSliding>
            <IonItemSliding>
              <IonItem href="https://www.google.com">
                <IonLabel>Item</IonLabel>
              </IonItem>
              <IonItemOptions side="end">
                <IonItemOption color="danger" onClick={() => {}}>Danger</IonItemOption>
              </IonItemOptions>
            </IonItemSliding>
          </IonList>
          <div className="footer-button">
            <IonButton expand="full" size="large" className="ion-align-self-end" type="submit">
              Receive
            </IonButton>
          </div>
        </form>
      </IonContent>
    </IonPage>
  );
};
export default FileReceive;