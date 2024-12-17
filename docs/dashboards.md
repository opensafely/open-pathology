# Dashboards

We will develop dashboards with [Streamlit][]
and deploy dashboards to the Streamlit [Community Cloud][].

In Community Cloud, a dashboard is known as an *app*
and an app corresponds to a Python file in a GitHub repository.

We will create apps in a shared account on Community Cloud,
the credentials for which are stored in [Bitwarden][];
the item name is "Streamlit Community Cloud".

Only members of the tech group have access to Bitwarden.
Consequently, whilst anyone in the OpenPathology team *could* create an app,
in practice, only members of the tech group should do so.

In Community Cloud, the shared account is known as a *Linked account*.
A linked account is different to a *source control account*,
which is an individual's GitHub account.
Consequently, to create an app, an individual should:

* login to Community Cloud with the shared account;
* login to GitHub with their individual account.

[Bitwarden]: https://bennett.wiki/tools-systems/bitwarden/
[Community Cloud]: https://streamlit.io/cloud
[Streamlit]: https://streamlit.io/
