from sklearn.preprocessing import MinMaxScaler, OneHotEncoder
import pandas as pd
from torch.utils.data.dataset import Dataset
import torch.utils.data
from torch.utils.data import DataLoader
from torch import nn
from sklearn.metrics import confusion_matrix


class HeartData(Dataset):
    def __init__(self, file_path):
        raw_data = pd.read_csv(file_path)
        x = raw_data.values[:, :-1]
        y = raw_data.values[:, -1]
        y = y.reshape(len(y), 1)
        one_hot_encoder = OneHotEncoder()
        min_max_scaler = MinMaxScaler()
        one_hot_encoder.fit(y)
        y = one_hot_encoder.transform(y).toarray()
        self.x = min_max_scaler.fit_transform(x)
        self.y = y

    def __len__(self):
        # e.g. len(x)
        return len(self.x)

    def __getitem__(self, idx):
        # e.g. foo[12]
        # idx would be 12 then
        return self.x[idx], self.y[idx]


def get_data(batch_size):
    heart_data = HeartData("heart disease/heart.csv")                                   #obtenemos el dataset del objeto

    training_data, test_data = torch.utils.data.random_split(
        heart_data,
        [int(len(heart_data) * 0.7), len(heart_data) - int(len(heart_data) * 0.7)],     #partimos el dataset en un 70% de entreno y un 30% de pruebas
    )
    train_dataloader = DataLoader(training_data, batch_size=batch_size, shuffle=True)   #y los guardamos en cada variable en partes segun la variable batch_size
    test_dataloader = DataLoader(test_data, batch_size=batch_size, shuffle=True)        #y desordenandolo
    return train_dataloader, test_dataloader    

# Define model
class NeuralNetwork(nn.Module):                     #definimos nuestra red neuronal como objeto
    def __init__(self):
        super().__init__()
        self.flatten = nn.Flatten()
        self.linear_relu_stack = nn.Sequential(     #la red en si funcionara con dos neuronas basadas en la funcion relu (leky relu en este caso)
            nn.Linear(13, 50),                      #y con tres capas lineales que pasaran del input de 13 del dataset a 50 y finalmente a un output de 2 (binario)
            nn.LeakyReLU(),
            nn.Linear(50, 50),
            nn.LeakyReLU(),
            nn.Linear(50, 2)
        )

    def forward(self, x):                           #definimos la funcion que ejecute la red como tal
        logits = self.linear_relu_stack(x)          
        return logits

def train(dataloader, model, loss_fn, optimizer):   #funcion de entrenamiento del modelo usando el mismo arquetipo usado en la red de MNIST
    size = len(dataloader.dataset)
    model.train()
    for batch, (X, y) in enumerate(dataloader):
        X, y = X.to(device), y.to(device)

        # Compute prediction error
        pred = model(X.to(torch.float32))           
        loss = loss_fn(pred, y)

        # Backpropagation
        optimizer.zero_grad()
        loss.backward()
        optimizer.step()

        if batch % 100 == 0:
            loss, current = loss.item(), batch * len(X)
            print(f"loss: {loss:>7f}  [{current:>5d}/{size:>5d}]")

def test(dataloader, model, loss_fn):               #funcion de test del modelo usando el mismo arquetipo usado en la red de MNIST
    size = len(dataloader.dataset)
    num_batches = len(dataloader)
    model.eval()
    test_loss, correct = 0, 0
    with torch.no_grad():
        lista0 = torch.zeros(2, 2 ,dtype=torch.float32) #creamos una lista de zeros de 2x2 para poder añadir los datos de la funcion confusion_matrix
        for X, y in dataloader:
            X, y = X.to(device), y.to(device)
            pred = model(X.to(torch.float32))
            test_loss += loss_fn(pred, y).item()
            correct += (pred.argmax(1) == y.argmax(1)).type(torch.float32).sum().item()     #importante asegurarnos que el type es el mismo que el que se esta usando en el modelo
            lista0 += confusion_matrix(y.argmax(1), pred.argmax(1))
    test_loss /= num_batches
    correct /= size
    print(f"Test Error: \n Accuracy: {(100*correct):>0.1f}%, Avg loss: {test_loss:>8f} \n")
    return (lista0)

#variables
batch_size = 32
learning_rate = 0.1
batch_size = 20
epochs = 60

# Create data loaders.
train_dataloader, test_dataloader = get_data(batch_size)

# Get cpu or gpu device for training.
device = "cuda" if torch.cuda.is_available() else "cpu"
model = NeuralNetwork().to(device)
loss_fn = nn.CrossEntropyLoss()
optimizer = torch.optim.SGD(model.parameters(), lr=learning_rate)

for t in range(epochs):
    print(f"Epoch {t+1}\n-------------------------------")
    train(train_dataloader, model, loss_fn, optimizer)
    tensoresult = test(test_dataloader, model, loss_fn)
print(tensoresult)
print ("Porcentaje de positivos reales en comparacion al total de positivos que hay:", int((tensoresult[0][0]/(tensoresult[0][0]+tensoresult[1][0]))*100), "%")
print ("Porcentaje de negativos reales en comparacion al total de negativos que hay:", int((tensoresult[1][1]/(tensoresult[1][1]+tensoresult[0][1]))*100), "%")


print("Done!")