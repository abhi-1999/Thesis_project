import pandas as pd
import torch
import gpytorch
import matplotlib.pyplot as plt


data = pd.read_excel('data_points.xlsx')
x_values = data.iloc[:, 0].values.reshape(-1, 1)  
y_values = data.iloc[:, 1].values


device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
x_train = torch.tensor(x_values, dtype=torch.float32, device=device)
y_train = torch.tensor(y_values, dtype=torch.float32, device=device)

class GPRegressionModel(gpytorch.models.ExactGP):
    def __init__(self, train_x, train_y, likelihood):
        super(GPRegressionModel, self).__init__(train_x, train_y, likelihood)
        self.mean_module = gpytorch.means.ConstantMean()
        self.covar_module = gpytorch.kernels.ScaleKernel(gpytorch.kernels.RBFKernel())

    def forward(self, x):
        mean_x = self.mean_module(x)
        covar_x = self.covar_module(x)
        return gpytorch.distributions.MultivariateNormal(mean_x, covar_x)

likelihood = gpytorch.likelihoods.GaussianLikelihood()
model = GPRegressionModel(x_train, y_train, likelihood).to(device)


model.train()
likelihood.train()

optimizer = torch.optim.Adam(model.parameters(), lr=0.1)

num_iterations = 100
for i in range(num_iterations):
    
    optimizer.zero_grad()
    
    output = model(x_train)
   
    loss = -likelihood(output, y_train).log_prob(y_train).mean()
    loss.backward()
    optimizer.step()


model.eval()
likelihood.eval()



with torch.no_grad(), gpytorch.settings.fast_pred_var():
    test_x = torch.linspace(min(x_values).item(), max(x_values).item(), 100, device=device)
    observed_pred = likelihood(model(test_x))


with torch.no_grad():
    plt.figure(figsize=(10, 6))
    plt.scatter(x_values, y_values, c='red', label='Data points')
    plt.plot(test_x.cpu().numpy(), observed_pred.mean.cpu().numpy(), color='blue', label='Predicted function')
    plt.fill_between(test_x.cpu().numpy(), observed_pred.mean.cpu().numpy() - 1.96 * observed_pred.variance.cpu().numpy(),
                     observed_pred.mean.cpu().numpy() + 1.96 * observed_pred.variance.cpu().numpy(), alpha=0.3, color='blue')
    plt.xlabel('x values')
    plt.ylabel('y values')
    
    plt.legend()
    plt.show()
